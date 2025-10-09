# Usage Examples

This directory contains example workflows demonstrating how to use the fabric-deploy-workflow for different scenarios.

## Example Workflows

### 1. `basic-workflow.yml` - Simple Manual Deployment
A basic workflow triggered manually with workflow_dispatch. Includes support for:
- Environment selection (dev/staging/prod)
- Deploy mode selection (auto/incremental/full)
- Dry run validation
- Manual approval through GitHub UI

**Use case**: Manual deployments with full control over deployment mode and target environment.

### 2. `incremental-deployment.yml` - Automated Incremental Deployments
Demonstrates automated incremental deployments on every push to main and PR validation:
- Automatic incremental deployment to dev on push to main
- PR validation with dry run mode
- Only triggers when Fabric artifacts change

**Use case**: Fast iteration in development with automatic change detection.

### 3. `multi-environment.yml` - Multi-Environment Pipeline
Shows deployment across multiple environments with environment-specific configuration:
- Auto mode deployment (incremental for dev/staging, full for prod)
- Environment-specific secrets and workspace IDs
- Optional staging deployment after dev success
- Dynamic secret and variable references

**Use case**: Production-ready pipeline with environment promotion and appropriate deployment modes.

### 4. `production-deployment.yml` - Production with Approval
Production-focused workflow with enhanced safety:
- Requires manual approval (GitHub environment protection)
- Defaults to full deployment for production safety
- Optional validation step before deployment
- Careful control over production deployments

**Use case**: Critical production deployments requiring approval and validation.

### 5. `branch-protected-deployment.yml` - Branch Protection Example
Demonstrates how to implement branch protection rules in your own workflow:
- Automatic environment detection based on branch name
- Configurable branch protection rules (main→prod, staging→staging, etc.)
- Force deployment option for emergency scenarios
- Clear error messages when protection rules are violated
- Pull request validation with dry-run mode

**Use case**: Organizations that need strict branch-to-environment controls.

### 6. `simple-auto-deploy.yml` - Simple Branch Mapping
Shows basic branch-to-environment mapping without complex protection:
- Automatic deployment based on branch (main→prod, staging→staging, dev→dev)
- Manual override support
- Minimal complexity for teams with simpler needs

**Use case**: Teams with simple deployment needs and trusted developers.

## Branch Protection Strategies

The reusable workflow is **environment agnostic** - it simply deploys to whatever environment you specify. **You control the branch protection logic** in your own workflow.
Production-focused workflow with enhanced safety:
- Requires manual approval (GitHub environment protection)
- Defaults to full deployment for production safety
- Optional validation step before deployment
- Careful control over production deployments

**Use case**: Critical production deployments requiring approval and validation.

## Deploy Mode Guide

### Auto Mode (Recommended)
- **Dev/Staging**: Uses incremental deployment for speed
- **Production**: Uses full deployment for safety
- Automatically selects the appropriate mode based on environment

### Incremental Mode
- Only deploys items that have changed in the source directory since last deployment
- Tracks deployment state using git tags (`latestDeployed/{environment}`)
- Ignores changes outside the source directory (documentation, workflows, etc.)
- Faster deployments with automatic change detection focused on Fabric artifacts
- Falls back to full deployment if git history is unavailable

### Full Mode
- Deploys all items regardless of changes
- Safer for production environments
- Slower but ensures complete deployment state
- Recommended for critical environments

## Getting Started

1. **Choose an example** that matches your deployment pattern
2. **Copy the workflow** to `.github/workflows/` in your repository
3. **Configure secrets** in your GitHub repository:
   - `AZURE_CLIENT_ID`
   - `AZURE_CLIENT_SECRET`
   - `AZURE_TENANT_ID`
4. **Set variables** for your Fabric workspace IDs
5. **Customize** the workflow for your specific needs

## Configuration Requirements

### Required Secrets
```
AZURE_CLIENT_ID               # Service Principal Application ID
AZURE_CLIENT_SECRET           # Service Principal Secret  
AZURE_TENANT_ID               # Azure Tenant ID

# For multi-environment (optional - can use environment-specific):
DEV_AZURE_CLIENT_ID           # Dev-specific Service Principal
DEV_AZURE_CLIENT_SECRET      
STAGING_AZURE_CLIENT_ID       # Staging-specific Service Principal
STAGING_AZURE_CLIENT_SECRET
PROD_AZURE_CLIENT_ID          # Production-specific Service Principal
PROD_AZURE_CLIENT_SECRET
```

### Required Variables
```
FABRIC_WORKSPACE_ID           # For single environment
DEV_FABRIC_WORKSPACE_ID       # For multi-environment
STAGING_FABRIC_WORKSPACE_ID
PROD_FABRIC_WORKSPACE_ID
```

### Repository Structure
```
your-repo/
├── .github/
│   └── workflows/
│       └── deploy.yml          # Your workflow
├── fabric-artifacts/           # Your Fabric items
│   ├── reports/
│   ├── datasets/
│   └── notebooks/
└── README.md
```

## Best Practices

1. **Environment Separation**: Use different Azure Service Principals and Fabric workspaces for each environment
2. **Deploy Mode Selection**: Use `auto` mode for most scenarios, override only when needed
3. **Change Detection**: Ensure your repository has proper git history for incremental deployments
4. **Validation**: Use dry run mode for PR validation and pre-deployment checks
5. **Production Safety**: Require manual approval for production deployments
6. **Monitoring**: Review deployment logs and handle failures appropriately

## Troubleshooting

- **Incremental deployment falls back to full**: Check git history and tag existence
- **Authentication failures**: Verify Service Principal permissions and secrets
- **No changes detected**: Ensure files in `source_directory` have actually changed
- **Deployment timeout**: Consider using incremental mode for large repositories