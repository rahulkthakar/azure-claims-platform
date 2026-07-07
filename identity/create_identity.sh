#!/usr/bin/env bash
# Creates Entra ID users + security groups entirely via CLI — no portal clicking.
# Run: az login   (once, opens browser)   then:   bash create_identity.sh
set -euo pipefail

DOMAIN=$(az ad signed-in-user show --query userPrincipalName -o tsv | cut -d'@' -f2)
echo "Using tenant domain: $DOMAIN"

# --- Users ---
az ad user create --display-name "QC Analyst" \
  --user-principal-name "qc.analyst@${DOMAIN}" \
  --password "ChangeMe!2026Temp" --force-change-password-next-sign-in true

az ad user create --display-name "PII Officer" \
  --user-principal-name "pii.officer@${DOMAIN}" \
  --password "ChangeMe!2026Temp" --force-change-password-next-sign-in true

az ad user create --display-name "BI Builder" \
  --user-principal-name "bi.builder@${DOMAIN}" \
  --password "ChangeMe!2026Temp" --force-change-password-next-sign-in true

# --- Groups ---
az ad group create --display-name "pii_readers" --mail-nickname "pii-readers"
az ad group create --display-name "qc_analysts" --mail-nickname "qc-analysts"
az ad group create --display-name "all_provinces" --mail-nickname "all-provinces"

# --- Membership ---
PII_OFFICER_ID=$(az ad user show --id "pii.officer@${DOMAIN}" --query id -o tsv)
QC_ANALYST_ID=$(az ad user show --id "qc.analyst@${DOMAIN}" --query id -o tsv)
PII_GROUP_ID=$(az ad group show --group pii_readers --query id -o tsv)
QC_GROUP_ID=$(az ad group show --group qc_analysts --query id -o tsv)

az ad group member add --group "$PII_GROUP_ID" --member-id "$PII_OFFICER_ID"
az ad group member add --group "$QC_GROUP_ID" --member-id "$QC_ANALYST_ID"

echo "Done. Created 3 users, 3 groups, and wired membership — zero portal clicks."
echo "Group Object IDs (needed later for Databricks/Power BI mapping):"
echo "  pii_readers   -> $PII_GROUP_ID"
echo "  qc_analysts   -> $QC_GROUP_ID"
