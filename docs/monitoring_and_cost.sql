-- Run in Databricks SQL editor. Turn the first query into a scheduled Alert
-- (SQL Editor -> Alerts -> New Alert), threshold: value > 5, schedule: hourly.

-- 1. Data quality watchdog
SELECT COUNT(*) AS quarantined_today
FROM azclaims.bronze.claims_quarantine
WHERE DATE(_ingested_at) = current_date();

-- 2. Freshness monitor
SELECT MAX(event_time) AS latest_event,
       TIMESTAMPDIFF(HOUR, MAX(event_time), current_timestamp()) AS hours_stale
FROM azclaims.silver.claims;

-- 3. Volume anomaly check
SELECT DATE(event_time) AS d, COUNT(*) AS c
FROM azclaims.silver.claims GROUP BY 1 ORDER BY 1 DESC LIMIT 7;

-- 4. Cost visibility (if system tables are enabled on your account)
-- SELECT * FROM system.billing.usage LIMIT 20;
