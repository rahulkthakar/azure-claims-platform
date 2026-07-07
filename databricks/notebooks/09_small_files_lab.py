# Databricks notebook source
# Manufacture the classic small-files problem, then fix it — the "observe, then act" method.
for i in range(50):
    spark.sql(f"""INSERT INTO azclaims.silver.claims VALUES
      ('TMP{i:03d}','P999','C999','AB','000-000-000',{100+i},'OPEN','2026-06-30T09:00:00')""")

before = spark.sql("DESCRIBE DETAIL azclaims.silver.claims").collect()[0]["numFiles"]
print("files BEFORE OPTIMIZE:", before)
spark.sql("OPTIMIZE azclaims.silver.claims")
after = spark.sql("DESCRIBE DETAIL azclaims.silver.claims").collect()[0]["numFiles"]
print("files AFTER OPTIMIZE:", after)
spark.sql("DELETE FROM azclaims.silver.claims WHERE claim_id LIKE 'TMP%'")
