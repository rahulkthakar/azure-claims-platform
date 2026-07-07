# Databricks notebook source
# Quality gate + dedupe: bad rows are QUARANTINED (never dropped), duplicates resolved
# by keeping the latest arrival per key — the Oracle "LOG ERRORS INTO" pattern, reborn.
spark.sql("""
CREATE TABLE IF NOT EXISTS azclaims.bronze.claims_quarantine (
  claim_id STRING, raw_record STRING, failure_reason STRING, _ingested_at TIMESTAMP)
""")

spark.sql("""
INSERT INTO azclaims.bronze.claims_quarantine
SELECT claim_id, to_json(struct(*)),
  CASE WHEN TRY_CAST(claim_amount AS DOUBLE) IS NULL THEN 'bad_amount'
       WHEN policy_id IS NULL OR policy_id = '' THEN 'missing_policy' END,
  current_timestamp()
FROM azclaims.bronze.claims_raw
WHERE TRY_CAST(claim_amount AS DOUBLE) IS NULL OR policy_id IS NULL OR policy_id = ''
""")

spark.sql("""
CREATE OR REPLACE TABLE azclaims.silver.claims AS
SELECT claim_id, policy_id, customer_id, province, sin,
       CAST(claim_amount AS DOUBLE) AS claim_amount, status,
       CAST(event_time AS TIMESTAMP) AS event_time
FROM (SELECT *, ROW_NUMBER() OVER (PARTITION BY claim_id ORDER BY _ingested_at DESC) rn
      FROM azclaims.bronze.claims_raw
      WHERE TRY_CAST(claim_amount AS DOUBLE) IS NOT NULL
        AND policy_id IS NOT NULL AND policy_id != '')
WHERE rn = 1
""")
display(spark.sql("SELECT failure_reason, count(*) FROM azclaims.bronze.claims_quarantine GROUP BY 1"))
