# Databricks notebook source
spark.sql("""
CREATE TABLE IF NOT EXISTS azclaims.silver.dim_customer (
  customer_id STRING, province STRING,
  effective_from TIMESTAMP, effective_to TIMESTAMP, is_current BOOLEAN)
""")
spark.sql("""
INSERT INTO azclaims.silver.dim_customer
SELECT DISTINCT customer_id, province, current_timestamp(), NULL, true
FROM azclaims.silver.claims
""")
# Simulate a customer moving province: close old row, insert new (SCD Type 2).
spark.sql("""
MERGE INTO azclaims.silver.dim_customer t
USING (SELECT 'C001' AS customer_id, 'ON' AS province) s
ON t.customer_id = s.customer_id AND t.is_current = true
WHEN MATCHED AND t.province != s.province THEN
  UPDATE SET is_current = false, effective_to = current_timestamp()
""")
spark.sql("INSERT INTO azclaims.silver.dim_customer SELECT 'C001','ON', current_timestamp(), NULL, true")
display(spark.sql("SELECT * FROM azclaims.silver.dim_customer WHERE customer_id='C001' ORDER BY effective_from"))
