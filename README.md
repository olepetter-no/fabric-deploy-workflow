# fabric-deploy-workflow

A lightweight, reusable GitHub workflow for deploying Microsoft Fabric solutions using Python and the `fabric-cicd` library.

[![CI](https://github.com/olepetter-no/fabric-deploy-workflow/actions/workflows/ci.yml/badge.svg)](https://github.com/olepetter-no/fabric-deploy-workflow/actions/workflows/ci.yml)

## Overview

This repository provides a **GitHub Workflow template** for deploying Microsoft Fabric artifacts (Reports, Notebooks, Lakehouses, etc.) to Fabric workspaces. Built on the official [`fabric-cicd`](https://github.com/microsoft/fabric-cicd) library.

**Key Features:**
- 🚀 **Incremental Deployments** - Deploy only changed items for faster iterations
- 🎯 **Smart Auto Mode** - Environment-aware deployment strategy selection
- 🔍 **Git-based Change Tracking** - Uses git tags to track deployment state
- 🛡️ **Dry-run Support** - Preview deployments without making changes
- 🎛️ **Selective Deployment** - Choose specific Fabric item types to deploy

## 🚀 Quick Start

### 1. Create Workflow File

Create `.github/workflows/fabric-deploy.yml` in your repository:

```yaml
name: Deploy to Microsoft Fabric

on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Target environment'
        type: choice
        options: ['dev', 'staging', 'prod']
        default: 'dev'
      dry_run:
        description: 'Perform dry run'
        type: boolean
        default: false

jobs:
  deploy:
    uses: olepetter-no/fabric-deploy-workflow/.github/workflows/fabric-deploy.yml@main
    with:
      fabric_workspace_id: ${{ vars.FABRIC_WORKSPACE_ID }}
      source_directory: './fabric-artifacts'
      environment: ${{ inputs.environment }}
      dry_run: ${{ inputs.dry_run }}
    secrets:
      AZURE_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
      AZURE_CLIENT_SECRET: ${{ secrets.AZURE_CLIENT_SECRET }}
      AZURE_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}
```

### 2. Setup Repository Structure

Organize your Fabric artifacts following the `fabric-cicd` convention:

```
your-repo/
├── fabric-artifacts/              # Source directory
│   ├── Notebooks/
│   │   └── DataProcessing.Notebook/
│   │       ├── .platform
│   │       └── notebook-content.py
│   ├── Reports/
│   │   └── SalesReport.Report/
│   │       ├── .platform
│   │       └── definition.json
│   └── Lakehouses/
│       └── DataLake.Lakehouse/
│           └── .platform
└── .github/workflows/
    └── fabric-deploy.yml
```

### 3. Configure Secrets and Variables

**Repository Secrets:**
- `AZURE_CLIENT_ID` - Service Principal Client ID
- `AZURE_CLIENT_SECRET` - Service Principal Client Secret
- `AZURE_TENANT_ID` - Azure Tenant ID

**Repository Variables:**
- `FABRIC_WORKSPACE_ID` - Target Fabric workspace ID (GUID)

## 📋 Configuration Options

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `fabric_workspace_id` | ✅ | - | Microsoft Fabric workspace ID (GUID) |
| `source_directory` | ❌ | `./fabric` | Directory containing Fabric artifacts |
| `environment` | ❌ | `dev` | Target environment (dev/staging/prod) |
| `deploy_mode` | ❌ | `auto` | Deployment mode: `full`, `incremental`, or `auto` |
| `dry_run` | ❌ | `false` | Preview deployment without making changes |
| `standardize_lakehouse_refs` | ❌ | `false` | Standardize lakehouse references in notebooks |
| `fabric_item_types` | ❌ | `""` | Comma-separated list of item types to deploy |

### Deployment Modes

- **`auto` (Recommended)**: Incremental for dev/staging, full for production
- **`incremental`**: Deploy only changed items (faster for development)
- **`full`**: Deploy all items (safer for production)

### Fabric Item Types

Control which artifact types to deploy by specifying `fabric_item_types`:

```yaml
# Deploy only notebooks and reports
fabric_item_types: "Notebook,Report"

# Deploy all types (default)
fabric_item_types: ""
```

**Supported Types**: `Notebook`, `DataPipeline`, `Environment`, `Report`, `SemanticModel`, `Lakehouse`, `Warehouse`, `KQLDatabase`

## 🛡️ Advanced Features

### Lakehouse Reference Standardization

Enable automatic standardization of lakehouse references for environment-specific deployments:

```yaml
with:
  standardize_lakehouse_refs: true
```

This replaces environment-specific lakehouse IDs with placeholders that get resolved via `parameter.yml` during deployment.

### Selective Item Deployment

Deploy only specific artifact types for faster, targeted deployments:

```yaml
# Example: Deploy only notebooks during development
with:
  fabric_item_types: "Notebook"
```

## 🔧 Local Development

### Prerequisites

- Python 3.12+
- Poetry
- Azure CLI (optional)

### Setup

```bash
git clone https://github.com/olepetter-no/fabric-deploy-workflow.git
cd fabric-deploy-workflow
poetry install
```

### CLI Usage

```bash
# Set Azure credentials
export AZURE_CLIENT_ID="your-client-id"
export AZURE_CLIENT_SECRET="your-client-secret"
export AZURE_TENANT_ID="your-tenant-id"

# Validate artifacts
poetry run fabric-deploy validate \
  --workspace-id "your-workspace-id" \
  --source-dir "./fabric-artifacts"

# Deploy with dry-run
poetry run fabric-deploy deploy \
  --workspace-id "your-workspace-id" \
  --source-dir "./fabric-artifacts" \
  --environment "dev" \
  --dry-run

# Deploy specific item types
poetry run fabric-deploy deploy \
  --workspace-id "your-workspace-id" \
  --source-dir "./fabric-artifacts" \
  --fabric-items Notebook \
  --fabric-items DataPipeline
```

## 📚 Examples

Common workflow patterns for different use cases:

### Manual Deployment (Recommended)
```yaml
on:
  workflow_dispatch:
    inputs:
      environment:
        type: choice
        options: ['dev', 'staging', 'prod']
      fabric_items:
        description: 'Item types to deploy (optional)'
        type: string
        default: ''
```

### Automatic CI/CD
```yaml
on:
  push:
    branches: [main]
    paths: ['fabric-artifacts/**']
```

### Pull Request Validation
```yaml
on:
  pull_request:
    paths: ['fabric-artifacts/**']
with:
  dry_run: true  # Always validate, never deploy
```

See [examples/](examples/) for complete workflow templates.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and test locally
4. Run pre-commit hooks: `poetry run pre-commit run --all-files`
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🆘 Support

- 📖 [Examples](examples/)
- 🐛 [Report Issues](https://github.com/olepetter-no/fabric-deploy-workflow/issues)
- 💬 [Discussions](https://github.com/olepetter-no/fabric-deploy-workflow/discussions)

---

**Built with ❤️ for the Microsoft Fabric community**
