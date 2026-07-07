"""Unit tests — run with: pytest databricks/tests -v
No Databricks connection needed; runs on local PySpark."""
from transforms import quarantine_reason, dedupe_latest


def test_bad_amount_flagged(spark):
    df = spark.createDataFrame(
        [("CL1", "P1", "not_a_number"), ("CL2", "P2", "100.0")],
        "claim_id string, policy_id string, claim_amount string")
    result = quarantine_reason(df).collect()
    reasons = {r["claim_id"]: r["failure_reason"] for r in result}
    assert reasons["CL1"] == "bad_amount"
    assert reasons["CL2"] is None


def test_missing_policy_flagged(spark):
    df = spark.createDataFrame(
        [("CL1", "", "100.0")],
        "claim_id string, policy_id string, claim_amount string")
    result = quarantine_reason(df).collect()
    assert result[0]["failure_reason"] == "missing_policy"


def test_zero_amount_is_not_a_parse_failure(spark):
    # Zero is a VALID number but a business-rule violation (kept simple here:
    # this test documents that quarantine_reason only classifies PARSE failures;
    # the business rule "amount > 0" is applied separately, e.g. in a WHERE clause).
    df = spark.createDataFrame(
        [("CL1", "P1", "0.0")],
        "claim_id string, policy_id string, claim_amount string")
    result = quarantine_reason(df).collect()
    assert result[0]["failure_reason"] is None  # parses fine; rule enforcement is a separate concern


def test_dedupe_keeps_latest(spark):
    df = spark.createDataFrame(
        [("CL1", 100, "2026-01-01"), ("CL1", 200, "2026-01-02"), ("CL2", 50, "2026-01-01")],
        "claim_id string, amount int, updated_at string")
    result = dedupe_latest(df, key="claim_id", order_col="updated_at").collect()
    amounts = {r["claim_id"]: r["amount"] for r in result}
    assert amounts["CL1"] == 200   # the Jan-2 row, not Jan-1
    assert amounts["CL2"] == 50
    assert len(result) == 2
