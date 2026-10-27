"""Reproducible synthetic decision analysis. No network or private data required."""
from pathlib import Path
import argparse, hashlib, json, logging, sqlite3
import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
KIND = "manufacturing"
SEED = 20261028

def generate_raw():
    rng = np.random.default_rng(SEED)
    if KIND == "manufacturing":
        n = 180 * 4
        dates = np.repeat(pd.date_range('2026-01-01', periods=180), 4)
        segments = np.tile(['Line A','Line B','Line C','Line D'],180)
        planned = rng.integers(420,481,n)
        downtime = np.minimum(planned, rng.gamma(2.2,13,n) + (segments=='Line C')*22)
        units = np.maximum(0, np.round((planned-downtime)*rng.uniform(1.6,2.0,n))).astype(int)
        defects = rng.binomial(units, .025 + (segments=='Line C')*.018)
        frame = pd.DataFrame(dict(observation_id=np.arange(1,n+1),date=dates,segment=segments,
            planned_minutes=planned,downtime_minutes=np.round(downtime,2),units=units,defects=defects))
    else:
        n = 12000
        dates = pd.Timestamp('2026-01-01') + pd.to_timedelta(rng.integers(0,90,n),unit='D')
        arm = rng.choice(['Control','Treatment'],n)
        converted = rng.binomial(1,.10+(arm=='Treatment')*.018)
        revenue = converted * rng.lognormal(7.1,.45,n)
        # Offer costs apply only to converted treatment customers; outreach cost applies to all treated.
        offer_cost = np.where(arm=='Treatment',converted*120+12,0)
        frame = pd.DataFrame(dict(observation_id=np.arange(1,n+1),date=dates,segment=arm,
            converted=converted,revenue=np.round(revenue,2),variable_cost=np.round(revenue*.58,2),
            offer_cost=offer_cost))
    # Explicit fixtures exercise duplicate, whitespace and invalid-numeric handling.
    frame['date'] = pd.to_datetime(frame['date']).dt.strftime('%Y-%m-%d')
    frame.loc[0,'segment'] = ' '+frame.loc[0,'segment']+' '
    frame = pd.concat([frame,frame.iloc[[9]]],ignore_index=True)
    invalid = frame.iloc[[10]].copy()
    invalid['observation_id'] = 999999
    invalid['downtime_minutes' if KIND=='manufacturing' else 'revenue'] = -5
    return pd.concat([frame,invalid],ignore_index=True)

def clean(frame):
    required = ['observation_id','date','segment'] + (['planned_minutes','downtime_minutes','units','defects']
        if KIND=='manufacturing' else ['converted','revenue','variable_cost','offer_cost'])
    missing = set(required)-set(frame.columns)
    if missing:
        raise ValueError(f'Missing columns: {sorted(missing)}')
    frame = frame[required].copy()
    frame['segment'] = frame['segment'].astype('string').str.strip()
    dates = pd.to_datetime(frame['date'],format='%Y-%m-%d',errors='coerce')
    frame['date'] = dates.dt.strftime('%Y-%m-%d')
    numeric = [c for c in required if c not in ['date','segment']]
    for col in numeric:
        frame[col] = pd.to_numeric(frame[col],errors='coerce')
    valid = frame.notna().all(axis=1) & np.isfinite(frame[numeric]).all(axis=1)
    valid &= (frame[numeric]>=0).all(axis=1) & (frame.observation_id>0)
    valid &= frame.observation_id.eq(np.floor(frame.observation_id))
    if KIND=='manufacturing':
        valid &= frame.segment.isin(['Line A','Line B','Line C','Line D'])
        valid &= (frame.planned_minutes>0)&(frame.downtime_minutes<=frame.planned_minutes)
        valid &= (frame.defects<=frame.units)
        valid &= frame.units.eq(np.floor(frame.units)) & frame.defects.eq(np.floor(frame.defects))
    else:
        valid &= frame.segment.isin(['Control','Treatment']) & frame.converted.isin([0,1])
        valid &= (frame.converted.eq(1) | frame.revenue.eq(0))
    rejects = frame.loc[~valid].copy()
    rejects['reason'] = 'invalid required value, category, numeric range or business constraint'
    accepted = frame.loc[valid].copy()
    # Identical retries may be dropped; conflicting rows with the same ID fail rather than silently overwrite.
    accepted = accepted.drop_duplicates()
    if accepted.observation_id.duplicated().any():
        raise ValueError('Conflicting records share an observation_id')
    return accepted.sort_values('observation_id'), rejects, int(valid.sum()-len(accepted))

def bootstrap_difference(a,b,rng,paired=False):
    results=[]
    for _ in range(2500):
        if paired:
            delta=a-b
            results.append(rng.choice(delta,len(delta),replace=True).mean())
        else:
            results.append(rng.choice(a,len(a),replace=True).mean()-rng.choice(b,len(b),replace=True).mean())
    return [float(x) for x in np.quantile(results,[.025,.975])]

def analyse(frame):
    rng=np.random.default_rng(SEED+1)
    if KIND=='manufacturing':
        # Day is the resampling unit, pairing line C to the other lines on the same day.
        daily=frame.assign(rate=frame.downtime_minutes/frame.planned_minutes).pivot(index='date',columns='segment',values='rate')
        a=daily['Line C'].to_numpy(); b=daily[['Line A','Line B','Line D']].mean(axis=1).to_numpy()
        delta=a-b
        null=np.array([np.mean(delta*rng.choice([-1,1],len(delta))) for _ in range(5000)])
        p=float((1+(np.abs(null)>=abs(delta.mean())).sum())/5001)
        summary=dict(project=KIND,synthetic=True,rows=len(frame),planned_minutes=float(frame.planned_minutes.sum()),
            downtime_minutes=float(frame.downtime_minutes.sum()),downtime_rate=float(frame.downtime_minutes.sum()/frame.planned_minutes.sum()),
            defect_rate=float(frame.defects.sum()/frame.units.sum()),
            primary_effect=float(delta.mean()),ci95=bootstrap_difference(a,b,rng,True),p_value=p,
            spearman_downtime_defects=float(frame.downtime_minutes.rank().corr((frame.defects/frame.units.replace(0,np.nan)).rank())))
        summary['decision']='Investigate Line C; require measured pilot before claiming savings.'
        frame['contribution']=frame.units-frame.defects
        groups=frame.groupby('segment',as_index=False).agg(planned_minutes=('planned_minutes','sum'),downtime_minutes=('downtime_minutes','sum'),units=('units','sum'),defects=('defects','sum'))
        groups['downtime_rate']=groups.downtime_minutes/groups.planned_minutes
        groups['defect_rate']=groups.defects/groups.units
    else:
        frame['contribution']=frame.revenue-frame.variable_cost-frame.offer_cost
        a=frame.loc[frame.segment.eq('Treatment'),'contribution'].to_numpy()
        b=frame.loc[frame.segment.eq('Control'),'contribution'].to_numpy()
        pool=np.concatenate([a,b]); observed=float(a.mean()-b.mean())
        null=[]
        for _ in range(5000):
            shuffled=rng.permutation(pool)
            null.append(shuffled[:len(a)].mean()-shuffled[len(a):].mean())
        p=float((1+(np.abs(null)>=abs(observed)).sum())/5001)
        ci=bootstrap_difference(a,b,rng)
        summary=dict(project=KIND,synthetic=True,rows=len(frame),primary_effect=observed,ci95=ci,p_value=p,
            control_mean=float(b.mean()),treatment_mean=float(a.mean()),
            converted=int(frame.converted.sum()),contribution=float(frame.contribution.sum()),
            allocation_treatment=int(frame.segment.eq('Treatment').sum()))
        summary['decision']='Pilot expansion only' if ci[0]>0 else 'Do not roll out; margin uplift is not demonstrated.'
        groups=frame.groupby('segment',as_index=False).agg(visitors=('observation_id','count'),converted=('converted','sum'),revenue=('revenue','sum'),contribution=('contribution','sum'))
        groups['conversion_rate']=groups.converted/groups.visitors
        groups['contribution_per_visitor']=groups.contribution/groups.visitors
    return frame,summary,groups

def run(input_path=None):
    for d in ['data/raw','data/processed','reports']:
        (BASE/d).mkdir(parents=True,exist_ok=True)
    raw = pd.read_csv(input_path) if input_path else generate_raw()
    raw.to_csv(BASE/'data/raw/observations.csv',index=False)
    clean_frame,rejects,duplicates=clean(raw)
    if clean_frame.empty:
        raise ValueError('No valid rows')
    frame,summary,groups=analyse(clean_frame)
    dates=pd.DataFrame({'date':sorted(frame.date.unique())})
    dates['date_key']=pd.to_datetime(dates.date).dt.strftime('%Y%m%d').astype(int)
    dates['month']=dates.date.str[:7]
    segments=pd.DataFrame({'segment':sorted(frame.segment.unique())})
    segments['segment_key']=np.arange(1,len(segments)+1)
    fact=frame.merge(dates[['date','date_key']],on='date',validate='many_to_one').merge(segments,on='segment',validate='many_to_one').drop(columns=['date','segment'])
    db_path=BASE/'data/warehouse.sqlite'
    # Transactional refresh keeps the previous committed DB valid if loading fails.
    with sqlite3.connect(db_path) as db:
        db.execute('PRAGMA foreign_keys=ON')
        db.executescript((BASE/'sql/schema.sql').read_text())
        with db:
            db.execute('DELETE FROM fact_observation'); db.execute('DELETE FROM dim_date'); db.execute('DELETE FROM dim_segment')
            for table,df in [('dim_date',dates),('dim_segment',segments),('fact_observation',fact)]:
                columns=','.join(df.columns)
                db.executemany(f'INSERT INTO {table} ({columns}) VALUES ({",".join("?" for _ in df.columns)})',df.itertuples(index=False,name=None))
        assert db.execute('SELECT COUNT(*) FROM fact_observation').fetchone()[0]==len(frame)
        assert not db.execute('PRAGMA foreign_key_check').fetchall()
        # Execute all analytical SQL, including CTEs and window functions.
        queries=(BASE/'sql/analysis.sql').read_text().split(';')
        for idx,query in enumerate(queries):
            if query.strip():
                pd.read_sql_query(query,db).to_csv(BASE/f'reports/sql_result_{idx+1}.csv',index=False)
    for table,df in [('dim_date',dates),('dim_segment',segments),('fact_observation',fact),('analysis_export',frame)]:
        df.to_csv(BASE/f'data/processed/{table}.csv',index=False)
    rejects.to_csv(BASE/'data/processed/rejects.csv',index=False)
    groups.to_csv(BASE/'reports/segment_summary.csv',index=False)
    summary['data_quality']=dict(raw_rows=len(raw),accepted_rows=len(frame),rejected_rows=len(rejects),identical_duplicates_removed=duplicates)
    summary['source_sha256']=hashlib.sha256((BASE/'data/raw/observations.csv').read_bytes()).hexdigest()
    (BASE/'reports/metrics.json').write_text(json.dumps(summary,indent=2,allow_nan=False))
    report=f"# Computed executive summary — SYNTHETIC\n\n{json.dumps(summary,indent=2)}\n\n"
    if KIND=='manufacturing':
        report+=f"Across {len(frame):,} simulated line-days, downtime consumed {summary['downtime_rate']:.1%} of planned time. Line C's mean daily downtime rate exceeded the mean of the other three lines by {summary['primary_effect']*100:.2f} percentage points (95% paired-day bootstrap interval {summary['ci95'][0]*100:.2f} to {summary['ci95'][1]*100:.2f}). Prioritize root-cause logging and a controlled maintenance pilot. This generator deliberately makes Line C worse; the result validates the analytical workflow, not an external operational discovery.\n"
    else:
        report+=f"Treatment minus control contribution per randomized visitor was INR {summary['primary_effect']:.2f} (95% bootstrap interval INR {summary['ci95'][0]:.2f} to {summary['ci95'][1]:.2f}). {summary['decision']} Conversion alone is not the rollout criterion. These are simulated economics, with an injected conversion effect and assumed costs, not a real campaign impact.\n"
    (BASE/'reports/EXECUTIVE_SUMMARY.md').write_text(report,encoding='utf-8')
    logging.info('Refresh complete: %s',summary['data_quality'])
    return summary

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,help='Optional CSV matching the documented contract; use anonymized data only')
    args=parser.parse_args()
    logging.basicConfig(level=logging.INFO,format='%(levelname)s %(message)s')
    run(args.input)
