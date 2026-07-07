# Databricks notebook source
# Real streaming ingestion with checkpointing (the SCN-bookmark equivalent).
stream = (spark.readStream.format("cloudFiles")
    .option("cloudFiles.format", "csv")
    .option("cloudFiles.schemaLocation", "/Volumes/azclaims/bronze/landing/_schema")
    .option("header", "true")
    .load("/Volumes/azclaims/bronze/landing/"))

q = (stream.writeStream
    .option("checkpointLocation", "/Volumes/azclaims/bronze/landing/_checkpoint")
    .trigger(availableNow=True)
    .toTable("azclaims.bronze.claims_autoloader"))
q.awaitTermination()
display(spark.sql("SELECT count(*) FROM azclaims.bronze.claims_autoloader"))
