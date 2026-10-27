-- Portable SQL subset: executed on SQLite; use equivalent types on PostgreSQL.
CREATE TABLE IF NOT EXISTS dim_date(date TEXT NOT NULL UNIQUE, date_key INTEGER PRIMARY KEY, month TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS dim_segment(segment TEXT NOT NULL UNIQUE, segment_key INTEGER PRIMARY KEY);
CREATE TABLE IF NOT EXISTS fact_observation(observation_id INTEGER PRIMARY KEY,
 planned_minutes REAL NOT NULL CHECK(planned_minutes>0),
 downtime_minutes REAL NOT NULL CHECK(downtime_minutes>=0 AND downtime_minutes<=planned_minutes),
 units INTEGER NOT NULL CHECK(units>=0),
 defects INTEGER NOT NULL CHECK(defects>=0 AND defects<=units),
 contribution REAL NOT NULL,
 date_key INTEGER NOT NULL REFERENCES dim_date(date_key),
 segment_key INTEGER NOT NULL REFERENCES dim_segment(segment_key));
CREATE INDEX IF NOT EXISTS idx_fact_date_segment ON fact_observation(date_key,segment_key);
