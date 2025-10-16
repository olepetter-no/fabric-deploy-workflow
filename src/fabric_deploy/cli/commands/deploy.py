import sys
from pathlib import Path

import click

from ...adapters.fabric_workspace import create_fabric_workspace_object
from ...adapters.azure_auth import get_azure_credential
from ...adapters.git_ops import GitOperations
from ...core import delta
from ...core import fabric_items
from ...core import deploy as deploy_core
from ...core.deploy import DeploymentResult
from ...core import lakehouse as lakehouse_core
from ...utils.logging import setup_logging


@click.command(help="Deploy artifacts to Microsoft Fabric.")
@click.option("--workspace-id", "workspace_id", required=True, help="Microsoft Fabric Workspace ID")
@click.option(
    "--source-directory",
    default="./fabric",
    show_default=True,
    help="Directory containing Fabric artifacts (must be inside a git repo)",
)
@click.option("--environment", required=True, help="Target environment (dev|staging|prod)")
@click.option(
    "--deploy-mode",
    type=click.Choice(["full", "incremental"], case_sensitive=False),
    default="full",
    show_default=True,
    help="full = deploy everything; incremental = deploy only changed items (via git tag)",
)
@click.option(
    "--unpublish-orphan-items",
    is_flag=True,
    default=True,
    show_default=True,
    help="Unpublish orphan items from the workspace.",
)
@click.option(
    "--standardize-default-lakehouse",
    is_flag=True,
    default=True,
    show_default=True,
    help="Standardize default lakehouse references in notebooks before deployment",
)
@click.option(
    "--update-tag/--no-update-tag",
    default=True,
    show_default=True,
    help="Maintain a git tag for last deployment to enable incremental mode.",
)
@click.option("--dry-run", is_flag=True, default=False, show_default=True, help="Perform a dry run without changes")
@click.option(
    "--verbose",
    is_flag=True,
    default=False,
    help="Enable verbose (debug-level) output.",
)
def cmd(
    workspace_id,
    source_directory,
    environment,
    dry_run,
    unpublish_orphan_items,
    deploy_mode,
    standardize_default_lakehouse,
    update_tag,
    verbose,
):
    """
    Orchestration:
      1) Show configuration, initialize logging, resolve paths
      2) Validate source directory (exists + inside a Git repo)
      3) Authenticate and create Fabric workspace clients
         - primary client for deployment
         - separate client for cleanup to avoid publish-time mutations
      4) Optionally standardize default lakehouse references in notebooks
      5) Determine deployment scope (full vs. incremental via git tag)
      6) Execute deployment
      7) Optionally unpublish orphan items
      8) Optionally update deployment tag
      9) Emit summary and exit with status
    """

    # --- Print selected settings ---
    click.echo("────────────────────────────────────────────────────────────────")
    click.echo("🚀 Deployment configuration:")
    click.echo(f"  Workspace ID:                    {workspace_id}")
    click.echo(f"  Environment:                     {environment}")
    click.echo(f"  Source directory:                {source_directory}")
    click.echo(f"  Mode:                            {deploy_mode}")
    click.echo(f"  Unpublish orphans:               {unpublish_orphan_items}")
    click.echo(f"  Standardize default lakehouse:   {standardize_default_lakehouse}")
    click.echo(f"  Update tag:                      {update_tag}")
    click.echo(f"  Dry run:                         {dry_run}")
    click.echo(f"  Verbose:                         {verbose}")
    click.echo("────────────────────────────────────────────────────────────────\n")

    setup_logging(verbose=verbose)
    src_dir = Path(source_directory).resolve()

    outputs: list[str] = []
    results: list[DeploymentResult] = []

    def record(res: DeploymentResult):
        results.append(res)
        outputs.append(res.message)

    # 1) sanity
    if not src_dir.exists() or not src_dir.is_dir():
        click.echo(f"Source directory not found: {src_dir}", err=True)
        sys.exit(2)

    # 2) Ensure source_directory has a git repo connected to it
    if not GitOperations.is_within_repo(src_dir):
        click.echo(f"Error: No Git repository found for source directory: '{src_dir}'")
        sys.exit(3)

    # 3) auth + workspace object
    creds = get_azure_credential()
    workspace = create_fabric_workspace_object(
        workspace_id=workspace_id,
        environment=environment,
        repo_directory=str(src_dir),
        credentials=creds,
    )
    ## Prevents the cleanup operation from being affected by changes to the workspace during publish
    clean_up_workspace = create_fabric_workspace_object(
        workspace_id=workspace_id,
        environment=environment,
        repo_directory=str(src_dir),
        credentials=creds,
    )

    # 4) optional lakehouse processing
    if standardize_default_lakehouse:
        lakehouse_core.apply(source_root=src_dir)

    # 5) selection (full vs incremental)
    changed_fabric_items = None
    mode = (deploy_mode or "full").lower()

    if mode == "incremental":
        if delta.is_initial_deployment(src_dir, environment):
            click.echo("No previous deployment tag found → performing initial FULL deployment.")
            mode = "full"
        else:
            changed_files = delta.get_changed_files(src_dir, environment, source_dir=str(src_dir))
            changed_fabric_items = fabric_items.extract_changed_items(paths=changed_files)
    # 6) deploy
    if mode == "incremental":
        if not changed_fabric_items:
            result = DeploymentResult(True, 0, "incremental", "ℹ️ No changed items detected for incremental deploy.")

        else:
            click.echo(f"Running incremental deploy. Number of items changed: {len(changed_fabric_items)}")
            result = deploy_core.run_incremental(
                workspace=workspace,
                changed_items=changed_fabric_items,
                dry_run=dry_run,
            )
    elif mode == "full":
        click.echo("Running full deploy")
        result = deploy_core.run_full(workspace=workspace, dry_run=dry_run)

    else:
        click.echo(f"Invalid deploy mode: {mode!r}. Must be 'full' or 'incremental'.", err=True)
        sys.exit(1)

    record(result)

    # 7) Unpublish items no longer connected to the repo
    if unpublish_orphan_items:
        unpublish_result = deploy_core.run_unpublish_orphans(workspace=clean_up_workspace, dry_run=dry_run)
        record(unpublish_result)

    # 8) optional tag update
    if update_tag:
        try:
            if dry_run:
                click.echo("[Dry run]: 🔄 would update deployment tag at HEAD")
            else:
                delta.update_tag(src_dir, environment)
        except RuntimeError as e:
            click.echo(f"Warning: failed to update deployment tag: {e}", err=True)

    # Final consolidated output
    all_ok = all(r.success for r in results) if results else True
    click.echo("\n".join(outputs))
    click.echo("✅ Deployment completed." if all_ok else "❌ Deployment finished with errors.")
    sys.exit(0 if all_ok else 1)
