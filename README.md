# fabric-deploy-workflow

A reusable GitHub workflow for deploying Microsoft Fabric solutions with incremental change tracking and environment isolation.

[![CI](https://github.com/olepetter-no/fabric-deploy-workflow/actions/workflows/ci.yml/badge.svg)](https://github.com/olepetter-no/fabric-deploy-workflow/actions/workflows/ci.yml)

---

## 🚀 Quick Start

Reference this workflow in your repository to deploy Fabric artifacts like Reports, Notebooks, Lakehouses, and Pipelines:

```yaml
# .github/workflows/deploy-dev.yml
name: Deploy to Development

on:
  workflow_dispatch:
    inputs:
      workspace_id:
        description: 'Microsoft Fabric workspace ID'
        required: true
        type: string

jobs:
  deploy:
    uses: olepetter-no/fabric-deploy-workflow/.github/workflows/fabric-deploy.yml@v1
    with:
      workspace_id: ${{ inputs.workspace_id }}
      source_directory: './fabric-artifacts'
      environment: 'dev'
    secrets:
      AZURE_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
      AZURE_CLIENT_SECRET: ${{ secrets.AZURE_CLIENT_SECRET }}
      AZURE_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}
```

---

## ✨ Key Features

- **� Incremental Deployments** - Deploy only changed artifacts using git tracking
- **🏷️ Environment Isolation** - Support for dev/staging/prod with separate configurations
- **🧪 Safe Testing** - Dry run mode and validation before deployment
- **🔗 Lakehouse Standardization** - Automatically fix lakehouse references
- **⚡ Selective Deployment** - Filter by Fabric item types (Reports, Notebooks, etc.)

---

## 📁 Repository Structure

Your repository should contain Fabric artifacts in the expected directory structure:

```
your-repo/
├── fabric-artifacts/          # ← Default source directory
│   ├── Notebooks/
│   │   └── MyNotebook.Notebook/
│   ├── Reports/
│   │   └── MyReport.Report/
│   ├── Lakehouses/
│   └── Pipelines/
└── .github/workflows/
    └── deploy-dev.yml
```

---

## ⚙️ Configuration

### Required Secrets
| Secret | Description |
|--------|-------------|
| `AZURE_CLIENT_ID` | Service Principal Client ID with Fabric permissions |
| `AZURE_CLIENT_SECRET` | Service Principal Secret |
| `AZURE_TENANT_ID` | Azure Active Directory Tenant ID |

### Workflow Inputs
| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| `workspace_id` | ✅ | - | Microsoft Fabric workspace ID (GUID) |
| `source_directory` | | `./fabric` | Directory containing Fabric artifacts |
| `environment` | ✅ | - | Target environment (dev/staging/prod) |
| `deploy_mode` | | `full` | Deployment mode: `full` or `incremental` |
| `standardize_default_lakehouse` | | `true` | Fix lakehouse references before deploy |
| `update_tag` | | `true` | Create git tags for incremental tracking |
| `dry_run` | | `false` | Preview changes without deploying |

---

## � Deployment Modes

### Full Deployment
Deploys all artifacts in the source directory regardless of changes:
```yaml
with:
  deploy_mode: 'full'
```

### Incremental Deployment
Deploys only artifacts changed since the last deployment tag:
```yaml
with:
  deploy_mode: 'incremental'
  update_tag: true  # Creates git tag for tracking
```

---

## �💻 Local Development

For testing and development, you can use the CLI directly:

```bash
# Clone and install
git clone https://github.com/olepetter-no/fabric-deploy-workflow.git
cd fabric-deploy-workflow
poetry install

# Validate artifacts
poetry run fabric-deploy validate \
  --workspace-id "your-workspace-id" \
  --source-directory "./fabric-artifacts" \
  --environment "dev"

# Test deployment (dry run)
poetry run fabric-deploy deploy \
  --workspace-id "your-workspace-id" \
  --source-directory "./fabric-artifacts" \
  --environment "dev" \
  --dry-run
```

---

## 📚 Examples

Ready-to-use workflow examples are available in the [`examples/`](./examples/) directory:

- **[`deploy-dev.yml`](./examples/deploy-dev.yml)** - Manual deployment to development
- **[`deploy-stage.yml`](./examples/deploy-stage.yml)** - Automatic staging deployment
- **[`deploy-prod.yml`](./examples/deploy-prod.yml)** - Production deployment with approval

---

## 🏷️ Versioning

Pin to a specific version for stability:

```yaml
uses: olepetter-no/fabric-deploy-workflow/.github/workflows/fabric-deploy.yml@v1.2.3
```

Or use a major version for automatic updates:

```yaml
uses: olepetter-no/fabric-deploy-workflow/.github/workflows/fabric-deploy.yml@v1
```

See [CHANGELOG.md](./CHANGELOG.md) for version history and migration guides.

---
