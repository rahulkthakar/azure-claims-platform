# Everything below is created with `terraform apply` from your terminal —
# zero portal clicking. This is the exact IaC discipline the JD asks for.
terraform {
  required_version = ">= 1.6"
  required_providers {
    azurerm = { source = "hashicorp/azurerm", version = "~> 3.100" }
  }
}

provider "azurerm" {
  features {}
}

locals {
  tags = {
    project = "azure-claims-platform"
    owner   = "rahul.thakar"
    env     = var.env
  }
}

resource "azurerm_resource_group" "rg" {
  name     = "${var.prefix}-rg"
  location = var.location
  tags     = local.tags
}

# Cost guardrail as code — same instinct as the OCI budget in the multicloud repo
resource "azurerm_consumption_budget_resource_group" "guard" {
  name              = "${var.prefix}-budget"
  resource_group_id = azurerm_resource_group.rg.id
  amount            = var.monthly_budget
  time_grain        = "Monthly"
  time_period {
    start_date = "${formatdate("YYYY-MM-01", timestamp())}T00:00:00Z"
  }
  notification {
    enabled        = true
    threshold      = 80
    operator       = "GreaterThan"
    contact_emails = [var.alert_email]
  }
}

resource "azurerm_storage_account" "lake" {
  name                     = replace("${var.prefix}lake", "-", "")
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  is_hns_enabled           = true # ADLS Gen2
  min_tls_version          = "TLS1_2"
  tags                     = local.tags
}

resource "azurerm_storage_container" "landing" {
  name                 = "landing"
  storage_account_name = azurerm_storage_account.lake.name
}

resource "azurerm_storage_container" "archive" {
  name                 = "archive"
  storage_account_name = azurerm_storage_account.lake.name
}

resource "azurerm_data_factory" "adf" {
  name                = "${var.prefix}-adf"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  tags                = local.tags
  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_databricks_workspace" "dbx" {
  name                = "${var.prefix}-dbx"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "premium" # premium = Unity Catalog / RBAC features
  tags                = local.tags
}
