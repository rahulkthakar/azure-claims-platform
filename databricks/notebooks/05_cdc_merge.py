# Databricks notebook source
# CDC apply — the GoldenGate Replicat translation: log-based changes applied via MERGE,
# with ROW_NUMBER doing the job trail-file ordering used to do (a micro-batch can carry
# several changes for one key; keep only the latest by commit_seq before applying).
spark.sql("ALTER TABLE azclaims.silver.claims SET TBLPROPERTIES (delta.enableChangeDataFeed = true)")

spark.sql("""
CREATE OR REPLACE TEMP VIEW day2 AS SELECT * FROM VALUES
 ('CL0001','P001','C001','QC','123-456-789','5500.00','CLOSED','2026-06-29T15:00:00','U',204),
 ('CL0002','P002','C002','ON','234-567-890', NULL,'CANCELLED','2026-06-29T11:00:00','D',202),
 ('CL9100','P045','C020','BC','345-678-901','7250.00','OPEN','2026-06-29T12:00:00','I',203)
 AS t(claim_id,policy_id,customer_id,province,sin,claim_amount,status,event_time,op,commit_seq)
""")

spark.sql("""
MERGE INTO azclaims.silver.claims t
USING (SELECT * FROM (SELECT *, ROW_NUMBER() OVER (PARTITION BY claim_id ORDER BY commit_seq DESC) rn
       FROM day2) WHERE rn = 1) s
ON t.claim_id = s.claim_id
WHEN MATCHED AND s.op = 'D' THEN DELETE
WHEN MATCHED THEN UPDATE SET claim_amount = CAST(s.claim_amount AS DOUBLE), status = s.status
WHEN NOT MATCHED AND s.op != 'D' THEN
  INSERT (claim_id, policy_id, customer_id, province, sin, claim_amount, status, event_time)
  VALUES (s.claim_id, s.policy_id, s.customer_id, s.province, s.sin,
          CAST(s.claim_amount AS DOUBLE), s.status, CAST(s.event_time AS TIMESTAMP))
""")

display(spark.sql("SELECT claim_id, _change_type FROM table_changes('azclaims.silver.claims', 2)"))
