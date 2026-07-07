#!/usr/bin/env bash
# Deploys the ADF pipeline definition above WITHOUT opening the ADF Studio UI.
# Run this from your terminal after `terraform apply` has created the Data Factory.
set -euo pipefail
RG="azclaims-rg"
ADF="azclaims-adf"

az config set extension.use_dynamic_install=yes_without_prompt

az datafactory linked-service create --resource-group azclaims-rg --factory-name azclaims-adf \
  --name AdlsLinkedService --properties @linked_service.json

az datafactory dataset create --resource-group azclaims-rg --factory-name azclaims-adf \
  --name LandingContainer --properties @ds_landing_container.json

az datafactory dataset create --resource-group azclaims-rg --factory-name azclaims-adf \
  --name LandingCsv --properties @ds_landing_csv.json

az datafactory dataset create --resource-group azclaims-rg --factory-name azclaims-adf \
  --name ArchiveParquet --properties @ds_archive_parquet.json
  
az datafactory pipeline create \
  --resource-group "$RG" \
  --factory-name "$ADF" \
  --name copy_claims_landing_to_archive \
  --pipeline @claims_copy_pipeline.json

echo "Pipeline deployed. Trigger a run with:"
echo "az datafactory pipeline create-run --resource-group $RG --factory-name $ADF --name copy_claims_landing_to_archive"
