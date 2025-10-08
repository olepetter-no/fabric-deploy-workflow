# Using fabric-deploy-workflow

Complete guide for using the `fabric-deploy-workflow` in your Microsoft Fabric projects. Two usage methods available!

## � Example Files

- **[`basic-workflow.yml`](basic-workflow.yml)** - Using the composite action (recommended for most users)
- **[`reusable-workflow.yml`](reusable-workflow.yml)** - Using the reusable workflow (advanced scenarios)

## �🚀 Quick Start

### Method 1: Simple Action Usage ⭐ **Most Popular**

**File**: [`basic-workflow.yml`](basic-workflow.yml)

Add to any workflow step:

```yaml
- name: Deploy to Microsoft Fabric
  uses: olepetter-no/fabric-deploy-workflow@main
  with:
    workspace_id: ${{ vars.FABRIC_WORKSPACE_ID }}
    source_directory: './fabric-artifacts'
    environment: 'prod'
  env:
    AZURE_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
    AZURE_CLIENT_SECRET: ${{ secrets.AZURE_CLIENT_SECRET }}
    AZURE_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}
```

### Method 2: Reusable Workflow Usage 🔧 **Advanced**

**File**: [`reusable-workflow.yml`](reusable-workflow.yml)

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

### 2. Repository Structure

Structure your repository following the `fabric-cicd` format:

```
your-repo/
├── .github/workflows/
│   └── fabric-deploy.yml              # Your workflow file
├── fabric-artifacts/                  # Source directory
│   ├── Reports/
│   │   └── SalesReport/
│   │       ├── item.metadata.json     # Item metadata
│   │       └── definition.json        # Report definition
│   ├── Notebooks/
│   │   └── DataProcessing/
│   │       ├── item.metadata.json
│   │       └── notebook-content.py
│   ├── Lakehouses/
│   │   └── DataLake/
│   │       ├── item.metadata.json
│   │       └── definition.json
│   └── Warehouses/
│       └── SalesWarehouse/
│           ├── item.metadata.json
│           └── definition.json
└── README.md
```

### 3. Item Metadata Format

Each Fabric item requires an `item.metadata.json` file:

```json
{
  "type": "Report",
  "displayName": "Sales Report",
  "description": "Monthly sales performance report"
}
```

Common item types:
- `Report` - Power BI reports
- `Notebook` - Fabric notebooks
- `Lakehouse` - Data lakehouses
- `Warehouse` - SQL warehouses
- `SemanticModel` - Datasets/semantic models
- `DataPipeline` - Data integration pipelines

## ⚙️ Configuration

### Repository Secrets

Add these secrets in your repository settings:

| Secret | Description | Example |
|--------|-------------|---------|
| `AZURE_CLIENT_ID` | Service Principal Client ID | `12345678-1234-1234-1234-123456789abc` |
| `AZURE_CLIENT_SECRET` | Service Principal Client Secret | `your-client-secret-here` |
| `AZURE_TENANT_ID` | Azure Tenant ID | `87654321-4321-4321-4321-cba987654321` |

### Repository Variables

Add these variables in your repository settings:

| Variable | Description | Example |
|----------|-------------|---------|
| `FABRIC_WORKSPACE_ID` | Target Fabric workspace ID | `11111111-2222-3333-4444-555555555555` |

### Service Principal Setup

Your Service Principal needs these permissions:
- **Fabric Admin** - For workspace access
- **Power BI Service Admin** - For report deployment
- **Contributor** - On the target Fabric workspace

## 🔧 Advanced Usage

### Complete Workflow Example (Action Method)

```yaml
name: Deploy to Multiple Environments

on:
  push:
    branches: [main, develop]
  workflow_dispatch:
    inputs:
      environment:
        description: 'Target environment'
        required: true
        default: 'dev'
        type: choice
        options: ['dev', 'staging', 'prod']
      dry_run:
        description: 'Perform dry run only'
        required: false
        default: false
        type: boolean

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
          environment: ${{ github.event.inputs.environment || (github.ref == 'refs/heads/main' && 'prod' || 'dev') }}
          dry_run: ${{ github.event.inputs.dry_run || false }}
        env:
          AZURE_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
          AZURE_CLIENT_SECRET: ${{ secrets.AZURE_CLIENT_SECRET }}
          AZURE_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}

      - name: Check deployment status
        if: always()
        run: |
          if [[ "${{ steps.deploy.outputs.deployment_status }}" == "success" ]]; then
            echo "✅ Deployment successful!"
          else
            echo "❌ Deployment failed: ${{ steps.deploy.outputs.error_message }}"
            exit 1
          fi
```

### Multi-Environment Deployment (Workflow Method)

```yaml
name: Deploy to Multiple Environments

on:
  push:
    branches: [main, develop]

jobs:
  deploy-dev:
    if: github.ref == 'refs/heads/develop'
    uses: olepetter-no/fabric-deploy-workflow/.github/workflows/fabric-deploy.yml@main
    with:
      fabric_workspace_id: ${{ vars.DEV_WORKSPACE_ID }}
      source_directory: './fabric-artifacts'
      environment: 'dev'
    secrets:
      AZURE_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
      AZURE_CLIENT_SECRET: ${{ secrets.AZURE_CLIENT_SECRET }}
      AZURE_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}

  deploy-prod:
    if: github.ref == 'refs/heads/main'
    uses: olepetter-no/fabric-deploy-workflow/.github/workflows/fabric-deploy.yml@main
    with:
      fabric_workspace_id: ${{ vars.PROD_WORKSPACE_ID }}
      source_directory: './fabric-artifacts'
      environment: 'prod'
    secrets:
      AZURE_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
      AZURE_CLIENT_SECRET: ${{ secrets.AZURE_CLIENT_SECRET }}
      AZURE_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}
```

### Pull Request Validation

```yaml
name: Validate Fabric Artifacts

on:
  pull_request:
    branches: [main]

jobs:
  validate:
    uses: olepetter-no/fabric-deploy-workflow/.github/workflows/fabric-deploy.yml@main
    with:
      fabric_workspace_id: ${{ vars.DEV_WORKSPACE_ID }}
      source_directory: './fabric-artifacts'
      environment: 'dev'
      dry_run: true  # Only validate, don't deploy
    secrets:
      AZURE_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
      AZURE_CLIENT_SECRET: ${{ secrets.AZURE_CLIENT_SECRET }}
      AZURE_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}
```

### Manual Deployment with Options

```yaml
name: Manual Fabric Deployment

on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Target environment'
        required: true
        default: 'dev'
        type: choice
        options:
        - dev
        - staging
        - prod
      dry_run:
        description: 'Perform dry run only'
        required: false
        default: false
        type: boolean

jobs:
  deploy:
    uses: olepetter-no/fabric-deploy-workflow/.github/workflows/fabric-deploy.yml@main
    with:
      fabric_workspace_id: ${{ vars.FABRIC_WORKSPACE_ID }}
      source_directory: './fabric-artifacts'
      environment: ${{ github.event.inputs.environment }}
      dry_run: ${{ github.event.inputs.dry_run }}
    secrets:
      AZURE_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
      AZURE_CLIENT_SECRET: ${{ secrets.AZURE_CLIENT_SECRET }}
      AZURE_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}
```

## 📁 Supported Fabric Items

The workflow supports all Microsoft Fabric item types:

| Item Type | Description | Metadata Example |
|-----------|-------------|------------------|
| **Report** | Power BI reports | `{"type": "Report", "displayName": "Sales Report"}` |
| **Notebook** | Fabric notebooks | `{"type": "Notebook", "displayName": "Data Processing"}` |
| **Lakehouse** | Data lakehouses | `{"type": "Lakehouse", "displayName": "Sales Data"}` |
| **Warehouse** | SQL warehouses | `{"type": "Warehouse", "displayName": "EDW"}` |
| **SemanticModel** | Datasets/models | `{"type": "SemanticModel", "displayName": "Sales Model"}` |
| **DataPipeline** | Data pipelines | `{"type": "DataPipeline", "displayName": "ETL Pipeline"}` |
| **Environment** | Spark environments | `{"type": "Environment", "displayName": "ML Environment"}` |
| **KQLDatabase** | KQL databases | `{"type": "KQLDatabase", "displayName": "Telemetry DB"}` |

## 🐛 Troubleshooting

### Common Issues

**Authentication Failed**
```
Error: Failed to authenticate with Azure
```
- Verify Service Principal credentials in repository secrets
- Check Service Principal has Fabric workspace permissions

**Workspace Not Found**
```
Error: Workspace with ID 'xxx' not found
```
- Verify `FABRIC_WORKSPACE_ID` variable is correct
- Ensure Service Principal has access to the workspace

**Invalid Artifact Structure**
```
Error: Missing item.metadata.json
```
- Ensure each artifact has `item.metadata.json` file
- Verify JSON format is valid

### Debug Mode

Enable debug logging by adding to your workflow:

```yaml
env:
  ACTIONS_STEP_DEBUG: true
  FABRIC_DEBUG: true
```

## 💡 Best Practices

1. **Use Dry Run First** - Always test with `dry_run: true` before actual deployment
2. **Environment Separation** - Use different workspaces for dev/staging/prod
3. **Version Control** - Tag releases for stable deployment versions
4. **Secret Management** - Rotate Service Principal secrets regularly
5. **Validation** - Use PR validation to catch issues early

## 📚 References

- [fabric-cicd Documentation](https://github.com/microsoft/fabric-cicd)
- [Microsoft Fabric Documentation](https://learn.microsoft.com/en-us/fabric/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
