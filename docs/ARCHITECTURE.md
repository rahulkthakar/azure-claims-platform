# Architecture

```
                 (real Entra ID users/groups via identity/create_identity.sh)
                                     |
 On-prem-style CSV ---> ADF pipeline (adf/) ---> ADLS Gen2 landing (terraform/)
                                     |                        |
                          Databricks Auto Loader      Microsoft Purview
                        (03_auto_loader_stream.py)    scans this same ADLS
                                     |                 source for enterprise
                                     v                 cataloging + PII
                    bronze.claims_raw  --quarantine-->  bronze.claims_quarantine
                                     |                 classification + a
                       MERGE (CDC apply,               business glossary term
                       05_cdc_merge.py)                 ("Open Exposure") —
                       + Change Data Feed               see note below.
                                     v
                            silver.claims  +  silver.dim_customer (SCD2)
                                     |
                     row filter + column mask (08_governance_masks.py)
                                     v
                         gold.fct_claims_daily (liquid clustering)
                                     v
                Power BI semantic model (DirectQuery + RLS, powerbi/)
```

Everything above is created by code or CLI — `terraform apply`, `az ad ...`,
`az datafactory pipeline create`, `databricks bundle deploy` — no portal clicking.
Only two things are manual by nature: Power BI Desktop's modeling canvas (a GUI
modeling tool, not something teams typically script), and the Purview scan
(a one-time enterprise-catalog exercise, not worth automating for a lab).

## On Purview specifically
Unity Catalog (inside Databricks, via `08_governance_masks.py`) enforces access
control, masks, and row filters WITHIN the lakehouse. Purview is the separate,
enterprise-wide catalog that scans EVERY source across the company — not just
Databricks — auto-classifies sensitive columns (like the `sin` column here),
and holds a shared business glossary so "what does Open Exposure mean" has one
answer company-wide. They're complementary: UC enforces inside the lakehouse,
Purview catalogs the whole estate.

**To reproduce the Purview scan yourself** (do this in one sitting — it bills
~$0.40/hr even idle, so delete the account the same evening):
1. Azure portal → create a Purview account (smallest size) in the `azclaims-rg`
   resource group Terraform already created.
2. Purview governance portal → Data Map → Register your `azclaims lake` storage
   account (grant its managed identity `Storage Blob Data Reader` on it) → New
   scan → run it.
3. Data Catalog → search the asset → confirm the `sin`-like column got an
   automatic classification hit.
4. Add one glossary term: "Open Exposure — sum of claim amounts on OPEN
   claims, owner: Claims Analytics" and link it to the `fct_claims_daily` asset.
5. Delete the Purview account before the day ends.

