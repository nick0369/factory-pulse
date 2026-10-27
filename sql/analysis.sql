-- Aggregate at one fact grain before joining/reporting. Rank segments by decision metric.
WITH segment_kpi AS (
SELECT s.segment, 1.0*SUM(f.downtime_minutes)/NULLIF(SUM(f.planned_minutes),0) AS metric, COUNT(*) AS observations
FROM fact_observation f JOIN dim_segment s ON f.segment_key=s.segment_key
GROUP BY s.segment)
SELECT *, DENSE_RANK() OVER(ORDER BY metric DESC) AS metric_rank FROM segment_kpi;
-- Monthly trend and change using a window, not self-join fanout.
WITH monthly AS (
SELECT d.month, 1.0*SUM(f.downtime_minutes)/NULLIF(SUM(f.planned_minutes),0) AS metric
FROM fact_observation f JOIN dim_date d ON f.date_key=d.date_key GROUP BY d.month)
SELECT *, metric-LAG(metric) OVER(ORDER BY month) AS absolute_change FROM monthly;
