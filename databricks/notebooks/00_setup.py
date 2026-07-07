# Databricks notebook source
# Creates the catalog/schema/volume skeleton. Run this first.
spark.sql("CREATE CATALOG IF NOT EXISTS azclaims")
spark.sql("CREATE SCHEMA IF NOT EXISTS azclaims.bronze")
spark.sql("CREATE SCHEMA IF NOT EXISTS azclaims.silver")
spark.sql("CREATE SCHEMA IF NOT EXISTS azclaims.gold")
spark.sql("CREATE VOLUME IF NOT EXISTS azclaims.bronze.landing")
print("catalog/schema/volume ready")
