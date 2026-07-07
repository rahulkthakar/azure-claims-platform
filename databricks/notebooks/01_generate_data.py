# Databricks notebook source
# Generates deliberately messy Day-1 claims data (duplicate, bad amount, missing policy)
# and lands it in the governed Volume.
import csv, io, random

random.seed(7)
rows = [["claim_id","policy_id","customer_id","province","sin","claim_amount","status","event_time"]]
for i in range(1, 201):
    rows.append([f"CL{i:04d}", f"P{random.randint(1,80):03d}", f"C{random.randint(1,50):03d}",
                 random.choice(["QC","ON","BC","AB"]),
                 f"{random.randint(100,999)}-{random.randint(100,999)}-{random.randint(100,999)}",
                 round(random.uniform(100, 25000), 2),
                 random.choice(["OPEN","OPEN","OPEN","CLOSED"]),
                 f"2026-06-{random.randint(1,28):02d}T{random.randint(8,18):02d}:00:00"])
rows.append(rows[5])  # exact duplicate — simulates a retry
rows.append(["CL9001","P010","C010","ON","111-222-333","not_a_number","OPEN","2026-06-15T09:00:00"])
rows.append(["CL9002","","C011","QC","222-333-444","500.00","OPEN","2026-06-16T10:00:00"])

buf = io.StringIO(); csv.writer(buf).writerows(rows)
dbutils.fs.put("/Volumes/azclaims/bronze/landing/claims_day1.csv", buf.getvalue(), overwrite=True)
print("landed day1:", len(rows) - 1, "rows")
