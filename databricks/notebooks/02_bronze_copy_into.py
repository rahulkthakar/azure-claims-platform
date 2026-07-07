# Databricks notebook source
spark.sql("""
CREATE TABLE IF NOT EXISTS azclaims.bronze.claims_raw (
  claim_id STRING, policy_id STRING, customer_id STRING, province STRING,
  sin STRING, claim_amount STRING, status STRING, event_time STRING,
  _source_file STRING, _ingested_at TIMESTAMP)
""")

spark.sql("""
COPY INTO azclaims.bronze.claims_raw
FROM (SELECT *, _metadata.file_name AS _source_file, current_timestamp() AS _ingested_at
      FROM '/Volumes/azclaims/bronze/landing/')
FILEFORMAT = CSV
FORMAT_OPTIONS ('header'='true')
COPY_OPTIONS ('mergeSchema'='true')
""")

# Idempotency proof: run again, count should not change.
spark.sql("""
COPY INTO azclaims.bronze.claims_raw
FROM (SELECT *, _metadata.file_name AS _source_file, current_timestamp() AS _ingested_at
      FROM '/Volumes/azclaims/bronze/landing/')
FILEFORMAT = CSV
FORMAT_OPTIONS ('header'='true')
COPY_OPTIONS ('mergeSchema'='true')
""")
display(spark.sql("SELECT count(*) AS row_count FROM azclaims.bronze.claims_raw"))
