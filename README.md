# Azure Claims Platform — End-to-End Lakehouse (Terraform + ADF + Databricks + Power BI)

A complete governed insurance-claims lakehouse on Azure Databricks, provisioned and deployed
**entirely as code** — Terraform for infra, CLI scripts for identity, JSON+CLI for ADF, an
Asset Bundle for Databricks jobs. No portal clicking anywhere except Power BI Desktop's modeling
canvas (a GUI tool by nature).

## What's here
```
terraform/         Resource group, cost budget, ADLS Gen2, Data Factory, Databricks workspace
identity/           Entra ID users + security groups via Azure CLI (az ad ...)
adf/                Copy pipeline as JSON + a CLI deploy script (no ADF Studio clicking)
databricks/
  notebooks/        00-09: setup, ingestion, quarantine, CDC/MERGE, SCD2, gold, masks, perf lab
  tests/            pytest unit tests for the pure transform functions (4/4 passing)
  databricks.yml    Asset Bundle — deploy the pipeline as a job with one command
powerbi/            DAX measures + step-by-step Desktop instructions (DirectQuery + RLS)
docs/
  ARCHITECTURE.md   One-page diagram of the whole platform
  monitoring_and_cost.sql   Data-quality alert + freshness/volume/cost queries
.github/workflows/ci.yml   Lint + unit tests + terraform validate, on every PR
```

## Run it, in order
```bash
# 1. Infrastructure
cd terraform
cp terraform.tfvars.example terraform.tfvars   # edit alert_email
terraform init && terraform plan && terraform apply

# 2. Identity
cd ../identity
az login
bash create_identity.sh

# 3. ADF pipeline
cd ../adf
bash deploy_pipeline.sh

# 4. Databricks — upload notebooks/ to your workspace and run 00 through 09 in order,
#    OR deploy the whole thing as a job:
cd ../databricks
databricks configure --host https://<your-workspace-url>
databricks bundle validate
databricks bundle deploy -t dev
databricks bundle run -t dev claims_pipeline

# 5. Tests (run anytime, no cloud needed)
cd tests && PYTHONPATH=. pytest test_transforms.py -v

# 6. Power BI — see powerbi/README.md
```

## Teardown (don't forget)
```bash
cd terraform && terraform destroy
```

See **docs/ARCHITECTURE.md** for the full diagram and **the companion teaching file**
(`TEACH_ME_20H.md`, provided alongside this repo) for an hour-by-hour build guide with every
concept explained from first principles.
