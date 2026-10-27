# Excel and Power BI implementation specification

## Import and model
Import `dim_date.csv`, `dim_segment.csv`, `fact_observation.csv` from `data/processed`. Each dimension has a one-to-many, single-direction relationship to its matching fact key. Set key columns to whole number; monetary/minute values to decimal; dates to Date. Disable auto date/time. Add a continuous calendar in Power BI if extending into time intelligence; supplied dates cover all simulation days but only dates actually present for external inputs. Mark the date table after verifying contiguous unique dates. Keep statistical confidence intervals and p-values on the full-population report; do not show unfiltered statistics under filtered slicers without a warning. DAX lives in `powerbi/measures.dax`. Zero denominator yields blank, never an artificial zero.

## Dashboard wireframe (1600 × 900)
Use 32 px outer margins, 20 px gutters, 12-column grid. White cards, navy headings, muted background; use orange only for exceptions. Every page shows SYNTHETIC BUSINESS SIMULATION and last refresh. Keyboard-friendly tab order, descriptive titles/alt text, no red/green-only encodings.

Page 1 / Decision brief: top 80 px title and decision; next 110 px KPI cards; middle 360 px two charts; bottom 220 px recommendation, quality checks, definitions. Right panel has date and line slicers plus reset button. Cards: downtime rate, defect rate, good units, rejected source rows. Main charts: ranked line downtime rates; daily downtime trend by line. Use weighted ratio totals rather than averaging segment percentages.

Page 2 / Root cause & audit: matrix rows line, columns month, measures raw denominators and rates; drill-through to individual observations; show source → rejects → duplicate removal → accepted reconciliation. Add report tooltip with exact denominator, unit and missing-value treatment. Do not infer a maintenance reason or marketing channel not in the data.

Page 3 / Statistical decision: import `reports/metrics.json` with Power Query and expand primary_effect, ci95 and p_value. Show an interval plot and zero reference; label global analysis, slicers do not recompute resampling. Display assumptions, resampling unit and recommendation. For manufacturing effects use percentage points, not relative percentages. For marketing effect use INR per randomized visitor. Do not present p-value as probability the hypothesis is true.

## Excel workflow (no workbook supplied)
Data → Get Data → From Text/CSV → `analysis_export.csv`; use `excel/import.pq` as a starter and replace PROJECT with repository name. Explicitly set all remaining measure fields numeric in Power Query. Load as table `Observations`. Create PivotTable rows segment, columns month (derive Date.Year/Month), values sums of numerator/denominator and observation counts. Add timeline/date and segment slicers. For weighted ratios either use the Data Model measures or divide pivot aggregate sums beside the pivot; never average row rates. Refresh All after rerunning Python.

Formula examples after loading the export as an Excel table:
`=SUM(Observations[downtime_minutes])/SUM(Observations[planned_minutes])` and `=IFERROR(SUM(Observations[defects])/SUM(Observations[units]),0)` (prefer a labelled blank for no production in reporting).
Use XLOOKUP on observation_id to inspect a disputed record and conditional formatting to flag invalid negative costs/time. Optional sensitivity input must be visibly labelled a scenario, never achieved results.

## Acceptance checklist
Compare dashboard totals to metrics.json and segment_summary.csv. Check filters, zero output, sums rather than averages, date sorting, negative formatting, relationships and drill-through. Show statistics only for the population they describe. Power BI Desktop/Service and Excel remain manual implementation steps; no PBIX or XLSX is included.
