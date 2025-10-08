# fabric-deploy-workflow

A lightweight, reusable GitHub workflow for deploying Microsoft Fabric solutions using Python and the `fabric-cicd` library.

[![CI](https://github.com/olepetter-no/fabric-deploy-workflow/actions/workflows/ci.yml/badge.svg)](https://github.com/olepetter-no/fabric-deploy-workflow/actions/workflows/ci.yml)

## Overview

This repository provides a **GitHub Action template** that other repositories can use to deploy Microsoft Fabric artifacts (Reports, Notebooks, Lakehouses, etc.) to Fabric workspaces. The deployment logic is implemented in Python using the official [`fabric-cicd`](https://github.com/microsoft/fabric-cicd) library.

## ✨ Features

- 🚀 **Reusable GitHub Action** - Use as a workflow template in any repository
- 🔧 **Simple Configuration** - Just workspace ID and source directory
- 🛡️ **Dry-run Support** - Validate deployments without making changes
- 📊 **Built-in Validation** - Pre-deployment validation of configuration
- 🔐 **Secure Authentication** - Azure Service Principal integration
- 📝 **Clear Logging** - Comprehensive deployment reporting
- ⚡ **Lightweight** - Minimal overhead, maximum efficiency

## 🚀 Quick Start

### Method 1: Simple Action Usage ⭐ **Recommended for most users**

Add a single step to your workflow:

```yaml
name: Deploy to Microsoft Fabric

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Deploy to Microsoft Fabric
        uses: olepetter-no/fabric-deploy-workflow@main
        with:
          workspace_id: ${{ vars.FABRIC_WORKSPACE_ID }}
          source_directory: './fabric-artifacts'
          environment: 'prod'
          dry_run: false
        env:
          AZURE_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
          AZURE_CLIENT_SECRET: ${{ secrets.AZURE_CLIENT_SECRET }}
          AZURE_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}
```

### Method 2: Reusable Workflow Usage 🔧 **For advanced scenarios**

Create `.github/workflows/fabric-deploy.yml` in your repository:

```yaml
name: Deploy to Microsoft Fabric

on:
  push:
    branches: [main]

jobs:
  deploy:
    uses: olepetter-no/fabric-deploy-workflow/.github/workflows/fabric-deploy.yml@main
    with:
      fabric_workspace_id: ${{ vars.FABRIC_WORKSPACE_ID }}
      source_directory: './fabric-artifacts'
      environment: 'prod'
    secrets:
      AZURE_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
      AZURE_CLIENT_SECRET: ${{ secrets.AZURE_CLIENT_SECRET }}
      AZURE_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}
```

### 2. Setup Repository Structure

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

## 📋 Action Inputs (for Method 1)

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| `workspace_id` | ✅ | - | Microsoft Fabric workspace ID (GUID) |
| `source_directory` | ❌ | `./fabric-artifacts` | Directory containing Fabric artifacts |
| `environment` | ❌ | `dev` | Target environment (dev/staging/prod) |
| `dry_run` | ❌ | `false` | Perform validation without deployment |

## 📋 Workflow Inputs (for Method 2)

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| `fabric_workspace_id` | ✅ | - | Microsoft Fabric workspace ID (GUID) |
| `source_directory` | ❌ | `./fabric` | Directory containing Fabric artifacts |
| `environment` | ❌ | `dev` | Target environment (dev/staging/prod) |
| `dry_run` | ❌ | `false` | Perform validation without deployment |
| `python_version` | ❌ | `3.12` | Python version to use |

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

## 🤔 Which Method Should I Use?

### **Use Method 1 (Action)** if you:
- ✅ Want the **simplest setup** possible
- ✅ Need to **combine** with other workflow steps
- ✅ Want **GitHub Marketplace discoverability**
- ✅ Prefer **single-step deployment**

### **Use Method 2 (Workflow)** if you:
- ✅ Need **advanced workflow features** (matrix builds, environments)
- ✅ Want **isolated job execution**
- ✅ Require **complex conditional logic**
- ✅ Prefer **dedicated deployment jobs**

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
