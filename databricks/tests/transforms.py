"""Pure transform functions extracted for unit testing — mirrors the pattern
in the streaming-pipeline repo: business logic lives in testable functions,
not buried in notebooks."""
from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def quarantine_reason(df: DataFrame) -> DataFrame:
    """Classify why a claims row would be quarantined. Mirrors 04_silver_quarantine.py."""
    return df.withColumn(
        "failure_reason",
        F.when(F.col("claim_amount").cast("double").isNull(), F.lit("bad_amount"))
         .when((F.col("policy_id").isNull()) | (F.col("policy_id") == ""), F.lit("missing_policy"))
         .otherwise(F.lit(None))
    )


def dedupe_latest(df: DataFrame, key: str, order_col: str) -> DataFrame:
    """Keep only the latest row per key — the ROW_NUMBER pattern used in every
    dedupe/CDC-apply step in this project."""
    from pyspark.sql.window import Window
    w = Window.partitionBy(key).orderBy(F.col(order_col).desc())
    return (df.withColumn("_rn", F.row_number().over(w))
              .where(F.col("_rn") == 1).drop("_rn"))
