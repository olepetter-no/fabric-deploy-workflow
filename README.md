# fabric-deploy-workflow

A lightweight, reusable GitHub workflow for deploying Microsoft Fabric solutions using Python and the `fabric-cicd` library.

[![CI](https://g# Deploy artifacts (incremental mode - only changed items)
poetry run fabric-deploy deploy \
  --workspace-id "your-workspace-id" \
  --source-dir "./fabric-artifacts" \
  --environment "dev" \
  --deploy-mode "incremental"

# Deploy artifacts (full mode - all items)
poetry run fabric-deploy deploy \
  --workspace-id "your-workspace-id" \
  --source-dir "./fabric-artifacts" \
  --environment "prod" \
  --deploy-mode "full"

# Deploy artifacts (auto mode - recommended)
export AZURE_CLIENT_ID="your-client-id"
export AZURE_CLIENT_SECRET="your-client-secret"  
export AZURE_TENANT_ID="your-tenant-id"

poetry run fabric-deploy deploy \
  --workspace-id "your-workspace-id" \
  --source-dir "./fabric-artifacts" \
  --environment "prod"ter-no/fabric-deploy-workflow/actions/workflows/ci.yml/badge.svg)](https://github.com/olepetter-no/fabric-deploy-workflow/actions/workflows/ci.yml)

## Overview

This repository provides a **GitHub Workflow template** that other repositories can use to deploy Microsoft Fabric artifacts (Reports, Notebooks, Lakehouses, etc.) to Fabric workspaces. The deployment logic is implemented in Python using the official [`fabric-cicd`](https://github.com/microsoft/fabric-cicd) library.

**Key Features:**
- **Incremental Deployments** - Deploy only changed items for faster iterations
- **Git-based Change Tracking** - Uses git tags to track deployment state
- **Environment-aware Defaults** - Auto mode chooses the best deployment strategy per environment

## ✨ Features

- 🚀 **Reusable GitHub Workflow** - Use as a workflow template in any repository
- ⚡ **Incremental Deployments** - Deploy only changed items for faster development cycles
- 🎯 **Smart Auto Mode** - Automatically chooses incremental (dev/staging) or full (prod) deployment
- 🔍 **Git-based Change Detection** - Uses git tags to track what's been deployed
- 🔧 **Simple Configuration** - Just workspace ID and source directory
- 🛡️ **Dry-run Support** - Simulate deployment behavior without making changes
- 📊 **Built-in Validation** - Pre-deployment validation of configuration
- 🔐 **Secure Authentication** - Azure Service Principal integration
- 📝 **Clear Logging** - Comprehensive deployment reporting
- ⚡ **Lightweight** - Minimal overhead, maximum efficiency

## 🚀 Quick Start

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
```### 2. Setup Repository Structure

Your repository should follow the standard `fabric-cicd` structure:

```
your-repo/
├── fabric-artifacts/              # Source directory
│   ├── Reports/
│   │   └── SalesReport/
│   │       ├── item.metadata.json
│   │       └── definition.json
│   ├── Notebooks/
│   │   └── DataProcessing/
│   │       ├── item.metadata.json
│   │       └── notebook-content.py
│   └── Lakehouses/
│       └── DataLake/
│           ├── item.metadata.json
│           └── definition.json
└── .github/workflows/
    └── fabric-deploy.yml          # Your workflow file
```

### 3. Configure Secrets and Variables

**Required Secrets:**
- `AZURE_CLIENT_ID` - Service Principal Client ID
- `AZURE_CLIENT_SECRET` - Service Principal Client Secret
- `AZURE_TENANT_ID` - Azure Tenant ID

**Required Variables:**
- `FABRIC_WORKSPACE_ID` - Target Fabric workspace ID

## 📋 Workflow Inputs

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| `fabric_workspace_id` | ✅ | - | Microsoft Fabric workspace ID (GUID) |
| `source_directory` | ❌ | `./fabric` | Directory containing Fabric artifacts |
| `environment` | ❌ | `dev` | Target environment (dev/staging/prod) |
| `dry_run` | ❌ | `false` | Simulate deployment behavior without making changes |
| `python_version` | ❌ | `3.12` | Python version to use |
| `deploy_mode` | ❌ | `auto` | Deployment mode: `full`, `incremental`, or `auto` |

## 🎯 Deployment Modes

### **Auto Mode (Recommended)** 🎯
- **Development/Staging**: Uses incremental deployment for fast iterations
- **Production**: Uses full deployment for reliability
- **Initial Deployment**: Always uses full deployment regardless of environment

### **Incremental Mode** ⚡
- Deploys only items that have changed in the source directory since last deployment
- Uses git tags (`latestDeployed/{environment}`) to track deployment state
- Ignores changes outside the source directory (documentation, workflows, etc.)
- Significantly faster for large repositories with many artifacts
- Perfect for development and staging environments

### **Full Mode** 🔄
- Deploys all items regardless of changes
- Ensures complete workspace synchronization
- Recommended for production deployments
- Slower but guarantees consistency

## 🛡️ Dry Run Mode

Dry run mode simulates deployment behavior without making actual changes. Perfect for:

- **Pre-deployment Testing** - See what would be deployed
- **Pull Request Validation** - Validate changes in CI/CD pipelines  
- **Change Impact Analysis** - Understand deployment scope

### Dry Run Output Examples

```bash
# Full deployment dry run
🔄 Dry run: Would perform FULL deployment of all items
📊 Dry run: Would deploy approximately 15 items from 4 categories
🧹 Dry run: Would remove orphaned items from workspace
🏷️  Dry run: Would update deployment tag: latestDeployed/prod

# Incremental deployment dry run  
⚡ Dry run: Would perform INCREMENTAL deployment
📊 Dry run: Found 3 changed files since last deployment
📊 Dry run: Mapped to 2 deployable items
📋 Dry run: Would deploy these items:
  ➤ Reports/SalesReport
  ➤ Notebooks/DataProcessing

# No changes dry run
📭 Dry run: No changes detected - no deployment needed
```

## 🏗️ Supported Fabric Items

This workflow supports all Fabric item types supported by `fabric-cicd`:

- **Reports** - Power BI reports (`.pbix` files)
- **Notebooks** - Fabric notebooks
- **Lakehouses** - Data lake storage
- **Warehouses** - SQL data warehouses
- **Datasets/Semantic Models** - Data models
- **DataPipelines** - Data integration pipelines
- **Environments** - Spark environments
- **KQL Databases** - Real-time analytics databases

## 🔧 Local Development

### Prerequisites

- Python 3.12+
- Poetry

### Setup

```bash
# Clone repository
git clone https://github.com/olepetter-no/fabric-deploy-workflow.git
cd fabric-deploy-workflow

# Install dependencies
poetry install

# Setup pre-commit hooks
poetry run pre-commit install
```

### CLI Usage

The Python package can be used standalone:

```bash
# Validate Fabric artifacts
poetry run fabric-deploy validate \
  --workspace-id "your-workspace-id" \
  --source-dir "./fabric-artifacts" \
  --environment "dev"

# Deploy artifacts (dry-run)
poetry run fabric-deploy deploy \
  --workspace-id "your-workspace-id" \
  --source-dir "./fabric-artifacts" \
  --environment "prod" \
  --dry-run

# Deploy artifacts (actual)
export AZURE_CLIENT_ID="your-client-id"
export AZURE_CLIENT_SECRET="your-client-secret"
export AZURE_TENANT_ID="your-tenant-id"

poetry run fabric-deploy deploy \
  --workspace-id "your-workspace-id" \
  --source-dir "./fabric-artifacts" \
  --environment "prod"
```

## 🤔 Usage Patterns

### **Manual Deployments** 🎯 **Recommended**
```yaml
on:
  workflow_dispatch:
    inputs:
      environment:
        type: choice
        options: ['dev', 'staging', 'prod']
      dry_run:
        type: boolean
        default: false
```

### **Automatic Deployments**
```yaml
on:
  push:
    branches: [main, develop]
  # Deploys automatically on push
```

### **Pull Request Validation**
```yaml
on:
  pull_request:
    branches: [main]
  # Always uses dry_run for validation
```

## 📚 Examples

See the [examples/](examples/) directory for:

- [Basic workflow](examples/basic-workflow.yml) - Simple deployment setup
- [Usage guide](examples/README.md) - Detailed configuration examples

## 🏗️ Architecture

```
fabric-deploy-workflow/
├── .github/workflows/
│   ├── fabric-deploy.yml      # Main reusable workflow
│   └── ci.yml                 # Repository CI/CD
├── src/fabric_deploy/
│   ├── cli/                   # Command-line interface
│   ├── core/                  # Core deployment logic
│   │   ├── deployer.py        # fabric-cicd integration
│   │   └── validator.py       # Pre-deployment validation
│   ├── models/                # Configuration models
│   └── utils/                 # Authentication & logging
├── examples/                  # Usage examples
└── pyproject.toml            # Python dependencies
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run pre-commit: `poetry run pre-commit run --all-files`
5. Test your changes: `poetry run fabric-deploy --help`
6. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](https://opensource.org/licenses/MIT).

## 🆘 Support

- 📖 [Documentation](examples/README.md)
- 🐛 [Report Issues](https://github.com/olepetter-no/fabric-deploy-workflow/issues)
- 💬 [Discussions](https://github.com/olepetter-no/fabric-deploy-workflow/discussions)

## 🔗 Related Projects

- [fabric-cicd](https://github.com/microsoft/fabric-cicd) - Official Microsoft Fabric CI/CD library
- [Microsoft Fabric Documentation](https://learn.microsoft.com/en-us/fabric/)

---

**Built with ❤️ for the Microsoft Fabric community**
