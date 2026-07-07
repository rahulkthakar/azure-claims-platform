# Databricks notebook source
spark.sql("""
CREATE OR REPLACE TABLE azclaims.gold.fct_claims_daily
CLUSTER BY (claim_date) AS
SELECT DATE(event_time) AS claim_date, province, status,
       COUNT(*) AS claim_count,
       ROUND(SUM(claim_amount),2) AS total_claim_amount,
       ROUND(AVG(claim_amount),2) AS avg_claim_amount
FROM azclaims.silver.claims
GROUP BY DATE(event_time), province, status
""")
spark.sql("""
CREATE OR REPLACE VIEW azclaims.gold.v_open_claims_by_province AS
SELECT province, SUM(total_claim_amount) AS open_exposure
FROM azclaims.gold.fct_claims_daily WHERE status='OPEN' GROUP BY province
""")
display(spark.sql("SELECT * FROM azclaims.gold.v_open_claims_by_province ORDER BY open_exposure DESC"))
