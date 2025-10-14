# Usage Examples

This folder shows how to use the **fabric-deploy-workflow** for Microsoft Fabric deployments across environments.

---

## Example Workflows

### 🧱 Development – `deploy-dev.yml`
Manual deployment to a dev workspace.
Supports:
- `deploy_mode` (full/incremental)
- Optional lakehouse standardization
- Optional tag updates

**Use:** Safe manual testing and early validation.

---

### 🧪 Staging – `deploy-stage.yml`
Automatic deployment on push to the `stage` branch.
Defaults to incremental mode for speed.
Requires environment approval (if configured).

**Use:** Continuous delivery to a staging workspace.

---

### 🚀 Production – `deploy-prod.yml`
Manual, protected workflow for production.
Only runs on the `main` branch.
Always performs full deployments with lakehouse standardization.

**Use:** Controlled, auditable production releases.

---

## How It Works

Each workflow calls the same reusable workflow:

```yaml
uses: olepetter-no/fabric-deploy-workflow/.github/workflows/fabric-deploy.yml@v1.0.0
```

It handles:
- Validation (`fabric-deploy validate`)
- Deployment (`fabric-deploy deploy`)
- Git tag tracking for incremental deploys

---

## Typical Branch Mapping

| Branch | Environment | Deploy Mode |
|:--------|:-------------|:-------------|
| `dev`   | Development  | Incremental  |
| `stage` | Staging      | Incremental  |
| `main`  | Production   | Full         |

---

## Setup

1. Copy the desired example workflow into `.github/workflows/`
2. Add secrets:
   - `AZURE_CLIENT_ID`
   - `AZURE_CLIENT_SECRET`
   - `AZURE_TENANT_ID`
3. Add environment variables:
   - `DEV_FABRIC_WORKSPACE_ID`
   - `STAGE_FABRIC_WORKSPACE_ID`
   - `PROD_FABRIC_WORKSPACE_ID`
4. Run manually or by branch trigger.

---

## Tips

- Use **incremental** for dev/stage, **full** for prod.
- Keep `update_deployment_tag` enabled for incremental tracking.
- Require **manual approval** for production environments.
- Pin to a release tag (e.g. `@v1.0.0`) for stable builds.

---

**Result:**
A simple, reusable deployment pipeline — fast for dev, safe for prod.
