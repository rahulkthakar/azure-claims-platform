# Power BI Desktop (Windows VM) — Real Semantic Model + RLS

You're on Windows now, so use Power BI **Desktop**, not the browser version — this is the
real production tool, and connects natively to a Databricks SQL warehouse.

## Steps
1. Install **Power BI Desktop** (Microsoft Store, free).
2. **Get Data → Azure Databricks**. Paste your workspace's SQL warehouse **Server hostname**
   and **HTTP path** (Databricks UI → SQL Warehouses → your warehouse → Connection details).
   Authenticate with Microsoft Entra ID (your `bi.builder` user from `identity/create_identity.sh`).
3. Select `azclaims.gold.fct_claims_daily` and `azclaims.gold.v_open_claims_by_province`. Load.
4. **Model view**: create a relationship if needed (here it's one flat fact table, so none required).
5. **New Measure** — paste each formula from `measures.dax`, one at a time.
6. **Modeling → Manage roles → New role** `QC_Only` → table filter: `[province] = "QC"`.
7. **Publish** to the Power BI Service (button in the top ribbon) — choose "My workspace."
8. In the Service (app.powerbi.com): dataset **Security** → add your `qc.analyst` user
   (created by the identity script) to the `QC_Only` role.
9. Build a report page: bar chart by province, line chart by claim_date, card for Open Exposure.
10. **Save the .pbix file into this folder before committing** (it's gitignored by default since
    .pbix is binary — remove that line in .gitignore if you want it version-controlled, or instead
    export a PDF of the report and save that as `powerbi/claims_dashboard.pdf` for the repo).

## Why DirectQuery here, not Import
Connecting live to the SQL warehouse (DirectQuery) means Unity Catalog row filters and column
masks apply automatically via SSO — the production pattern. Import mode (uploading a CSV) is
the fallback if the native connector needs extra workspace configuration you haven't set up.
