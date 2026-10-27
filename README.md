# FactoryPulse: downtime and quality decision system

Independent portfolio project by Nikhil Chandekar. **Synthetic data; no employer delivery, realised savings or live dashboard claimed.**

A fictional four-line manufacturer has inconsistent downtime reports and needs to prioritize a maintenance investigation. 

## Run locally
Python 3.11 or newer recommended. The pinned dependency versions were verified with the bundled Python in the delivery environment.
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python src/pipeline.py
python -m unittest discover -s tests
```
The run is offline and deterministic. It creates a SQLite warehouse, rejects, Power BI/Excel CSV exports, SQL results and a computed statistical executive summary. Rerunning replaces the same snapshot without double-counting. To ingest a matching anonymized file: `python src/pipeline.py --input /path/to/observations.csv`. See [contract and methodology](docs/CASE_STUDY.md).

## Results and decision
[Computed executive summary](reports/EXECUTIVE_SUMMARY.md) · [Segment results](reports/segment_summary.csv) · [Machine-readable metrics](reports/metrics.json).

## Architecture
`src/pipeline.py` → `sql/schema.sql` → `data/warehouse.sqlite` → `data/processed/*.csv` → Excel/Power BI.
`sql/analysis.sql` demonstrates joins, grouping, CTEs, LAG and ranking. Invalid records are quarantined; conflicting identifiers fail. Source SHA-256 and row reconciliation are recorded. [Business case](docs/CASE_STUDY.md) covers assumptions, metrics and recommendations. [Dashboard and Excel guide](docs/DASHBOARD_AND_EXCEL.md) covers model, DAX, Power Query, layouts and validation.

## Repository map
```text
src/             Ingestion, cleaning, SQL load, statistics, exports
sql/             Constraints, star schema, analytical queries
data/processed/  Synthetic sample exports and rejects
reports/         Computed results, quality metrics and recommendations
powerbi/         DAX measures (manual report implementation)
excel/           Power Query starter (manual workbook implementation)
docs/            Business case and dashboard specifications
tests/           Data contract and statistical edge checks
.github/         CI definition
```

## Publishing
Create a new GitHub repo named `factory-pulse`. Upload this folder's contents; do not upload private raw data, credentials, `.venv` or local database. Add a report screenshot only after manually building and validating it. CI executes the pipeline and checks. A hosted demo can publish static report content; Python needs a separate runtime if refreshed online. Production deployment, monitoring and access controls are not included. MIT licence covers original code and generated synthetic examples. Employer JDs are linked for research and are not included as copied datasets.

## Interview explanation
Start with the business decision, then grain and denominators, dirty-data handling, SQL reconciliation, choice of resampling unit, confidence interval, and action. Explain one limitation and the next validation you would run. Do not claim a Power BI report has been built from this specification alone.
