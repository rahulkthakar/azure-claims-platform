ADF_MI=$(az datafactory show --resource-group azclaims-rg --name azclaims-adf --query identity.principalId -o tsv)
echo [$ADF_MI]

STORAGE_ID=$(az storage account show --resource-group azclaims-rg --name azclaimslake --query id -o tsv)
echo [$STORAGE_ID]

MSYS_NO_PATHCONV=1

az role assignment create \
  --assignee "${ADF_MI}" \
  --role "Storage Blob Data Contributor" \
  --scope "${STORAGE_ID}"

sleep 120