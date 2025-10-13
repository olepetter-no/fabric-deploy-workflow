# fabric-deploy-workflow

A lightweight, reusable GitHub workflow for deploying Microsoft Fabric solutions using Python and the `fabric-cicd` library.

[![CI](https://github.com/olepetter-no/fabric-deploy-workflow/actions/workflows/ci.yml/badge.svg)](https://github.com/olepetter-no/fabric-deploy-workflow/actions/workflows/ci.yml)

---

## 🚀 Overview

This repository provides a **reusable GitHub workflow and CLI** for deploying Microsoft Fabric artifacts such as Reports, Notebooks, Lakehouses, and Pipelines — built on top of [microsoft/fabric-cicd](https://github.com/microsoft/fabric-cicd).

### Key Features
- **Incremental or Full Deployments**
- **Git-based Change Tracking**
- **Lakehouse Reference Standardization**
- **Dry Run Mode**
- **Reusable Workflow for Any Environment**

---

## ⚙️ Quick Setup

### 1. Create a Workflow File

Example: `.github/workflows/deploy-dev.yml`

```yaml
name: Deploy to Development

on:
  workflow_dispatch:
    inputs:
      workspace_id:
        description: 'Microsoft Fabric workspace ID'
        required: true
        type: string
      deploy_mode:
        description: 'Deployment mode'
        type: choice
        options: ['full', 'incremental']
        default: 'full'
      standardize_lakehouse_refs:
        description: 'Standardize lakehouse references'
        type: boolean
        default: false
      update_deployment_tag:
        description: 'Update git deployment tags for incremental tracking'
        type: boolean
        default: true

jobs:
  deploy-development:
    uses: olepetter-no/fabric-deploy-workflow/.github/workflows/fabric-deploy.yml@v1
    with:
      fabric_workspace_id: ${{ inputs.workspace_id }}
      source_directory: './fabric-artifacts'
      environment: 'dev'
      deploy_mode: ${{ inputs.deploy_mode }}
      standardize_lakehouse_refs: ${{ inputs.standardize_lakehouse_refs }}
      update_deployment_tag: ${{ inputs.update_deployment_tag }}
    secrets:
      AZURE_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
      AZURE_CLIENT_SECRET: ${{ secrets.AZURE_CLIENT_SECRET }}
      AZURE_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}
```

> 💡 Use a version tag (e.g., `@v1`) for stability.

---

### 2. Repository Structure

```
your-repo/
├── fabric-artifacts/
│   ├── Notebooks/
│   │   └── Example.Notebook/
│   ├── Reports/
│   └── Lakehouses/
└── .github/workflows/
    └── deploy-dev.yml
```

---

## 🔐 Required Configuration

### Secrets
| Name | Description |
|------|--------------|
| `AZURE_CLIENT_ID` | Azure Service Principal Client ID |
| `AZURE_CLIENT_SECRET` | Azure Service Principal Secret |
| `AZURE_TENANT_ID` | Azure Tenant ID |

### Variables
| Name | Description |
|------|--------------|
| `FABRIC_WORKSPACE_ID` | Microsoft Fabric workspace ID (GUID) |

---

## 💻 Local Development

```bash
git clone https://github.com/olepetter-no/fabric-deploy-workflow.git
cd fabric-deploy-workflow
poetry install
```

### CLI Usage

```bash
# Validate
poetry run fabric-deploy validate   --workspace-id "your-workspace-id"   --source-directory "./fabric-artifacts"   --environment "dev"

# Deploy (dry run)
poetry run fabric-deploy deploy   --workspace-id "your-workspace-id"   --source-directory "./fabric-artifacts"   --environment "dev"   --dry-run
```

---

## 🧱 Example Workflows

| File | Description |
|------|--------------|
| `deploy-dev.yml` | Manual deployment to dev |
| `deploy-stage.yml` | Auto deploy on stage branch |
| `deploy-prod.yml` | Full deploy from main with approval |
| `release.yml` | Tag and release version workflow |

---
