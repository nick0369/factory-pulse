# FactoryPulse: downtime and quality decision system

## Problem and decision
A fictional four-line manufacturer has inconsistent downtime reports and needs to prioritize a maintenance investigation. Stakeholders: plant manager, maintenance lead, quality engineer and finance partner. Decide which line to investigate first without confusing throughput, defects and time loss. Grain: one line per calendar day; 180 days, four lines, one comparable planned production period per day. Currency is not used in observed KPIs. Success targets (proposed, not achieved): complete daily reconciliation, under 1% invalid input, at least 95% refresh reliability, and a pilot that reduces downtime without raising defect rates. Do not call the proxy below OEE: ideal-cycle-time and availability/performance/quality components are not fully observed.

## Executive summary
Read [the computed executive summary](../reports/EXECUTIVE_SUMMARY.md) for actual generated values and confidence intervals. This file deliberately does not hard-code improved savings. All observations are synthetic and the generator injects known differences. Business impact is a proposed decision process, not a delivered employer result.

## Stakeholder acceptance
Owner signs off KPI dictionary and grain; reconcile accepted + rejected + duplicate rows to source; reconcile SQL totals to exported fact; verify empty-filter/zero-denominator behavior; show uncertainty beside decision; record refresh date and synthetic label. A production success score requires an actual pilot and agreed costs, neither provided here.

## Source and pipeline
Run `python src/pipeline.py` for seeded local simulation; `--input path/to/file.csv` replaces the fixture with matching anonymized input. Never overwrite the packaged sample with private customer data for public publishing. Pipeline: raw CSV snapshot → required-field/type/range checks → reject invalid rows → drop identical retries → fail conflicting IDs → derive decision metrics → star schema → transactionally reload SQLite → CSV exports → statistical report. Raw files are ignored by Git, processed synthetic examples are provided. No external data licence or download required. No PII in simulation.

## Schema and data dictionary
`dim_date`: unique date_key YYYYMMDD, date ISO-8601, month YYYY-MM. `dim_segment`: unique integer segment_key and line/assignment name. `fact_observation`: unique observation_id, two dimension keys, numeric measures. No bidirectional or many-to-many relationships. Schema constraints in `sql/schema.sql` enforce nonnegative measures and referential integrity.
planned_minutes: scheduled production minutes; downtime_minutes: time unavailable inside that schedule; units: all produced units; defects: rejected units, subset of units; contribution: good-unit count (units minus defects), not financial contribution. Zero output is allowed; defect rate then blank.

## Statistical design and justification
Pre-specified primary comparison: daily Line C downtime rate minus the same-day mean of Lines A/B/D. Use 2,500 paired-day bootstrap samples for the 95% percentile interval and 5,000 paired sign flips for a two-sided approximate null test (finite Monte Carlo correction). Pairing controls shared date conditions; assumes independent days and symmetric daily differences under the null. If serial correlation exists, use a moving-block bootstrap and randomized operational pilot instead. Line C was selected before analysis, not chosen post hoc. Other rankings and Spearman rank correlation between downtime and defect fraction are exploratory and descriptive. Correlation can reflect line mix and does not show causality. No currency savings are claimed. Translate a proposed 10% downtime reduction into recovered minutes only, then validate bottleneck capacity and finance-approved contribution before monetizing.

## Recommendations
Investigate maintenance causes on Line C first, audit downtime reason codes, and introduce a small controlled maintenance pilot. Quality leader monitors defects per produced unit. Compare like-for-like planned periods and record demand constraints. Do not estimate lost sales from all recovered minutes. Revisit prioritization after new causal pilot data.

## Operational readiness and limits
Production-oriented starter, not a deployed enterprise system. Uses local full refresh; add scheduler, restricted credentials, monitoring, encryption, retention policy, schema migrations, incremental watermarks, retries and backfills for real deployments. Record business timezone at ingestion; synthetic inputs use date only. Late-arriving outcomes require a completeness watermark. Bootstrap intervals are statistical uncertainty under assumptions, not uncertainty about a made-up generator. No live Power BI report, PBIX, Excel workbook or external deployment is claimed.
