# Databricks notebook source
# Column mask = Data Redaction reborn; row filter = VPD reborn.
# Both check REAL Entra-synced group membership (see identity/create_identity.sh).
spark.sql("""
CREATE OR REPLACE FUNCTION azclaims.silver.mask_sin(sin STRING)
RETURN CASE WHEN is_account_group_member('pii_readers') THEN sin
            ELSE CONCAT('XXX-XXX-', RIGHT(sin, 3)) END
""")
spark.sql("ALTER TABLE azclaims.silver.claims ALTER COLUMN sin SET MASK azclaims.silver.mask_sin")

spark.sql("""
CREATE OR REPLACE FUNCTION azclaims.silver.qc_only(province STRING)
RETURN is_account_group_member('all_provinces') OR province = 'QC'
""")
spark.sql("ALTER TABLE azclaims.silver.claims SET ROW FILTER azclaims.silver.qc_only ON (province)")

display(spark.sql("SELECT claim_id, sin, province FROM azclaims.silver.claims LIMIT 5"))

# Drop the row filter so later notebooks see all data:
spark.sql("ALTER TABLE azclaims.silver.claims DROP ROW FILTER")
