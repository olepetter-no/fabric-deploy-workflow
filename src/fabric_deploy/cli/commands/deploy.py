import sys
from pathlib import Path

import click

from ...adapters.fabric_workspace import create_fabric_workspace_object
from ...adapters.identity_azure import get_azure_credential
from ...core import delta
from ...core import deploy as deploy_core
from ...core import lakehouse as lakehouse_core
from ...utils.logging import setup_logging


@click.command(help="Deploy artifacts to Microsoft Fabric.")
@click.option("--fabric-workspace-id", "workspace_id", required=True, help="Microsoft Fabric Workspace ID")
@click.option(
    "--source-directory",
    default="./fabric",
    show_default=True,
    help="Directory containing Fabric artifacts (must be inside a git repo)",
)
@click.option("--environment", required=True, help="Target environment (dev|staging|prod)")
@click.option("--dry-run", is_flag=True, default=False, show_default=True, help="Perform a dry run without changes")
@click.option(
    "--deploy-mode",
    type=click.Choice(["full", "incremental"], case_sensitive=False),
    default="full",
    show_default=True,
    help="full = deploy everything; incremental = deploy only changed items (via git tag)",
)
@click.option(
    "--standardize-lakehouse-refs",
    is_flag=True,
    default=False,
    show_default=True,
    help="Standardize lakehouse references in notebooks before deployment",
)
@click.option(
    "--update-deployment-tag/--no-update-deployment-tag",
    default=True,
    show_default=True,
    help="Maintain a git tag for last deployment to enable incremental mode.",
)
def cmd(
    workspace_id,
    source_directory,
    environment,
    dry_run,
    deploy_mode,
    standardize_lakehouse_refs,
    update_deployment_tag,
):
    """
    Orchestration:
      1) Resolve paths, setup logging
      2) Prepare FabricWorkspace
      3) full vs incremental selection (git tag based)
      4) optional lakehouse standardization
      5) deploy
      6) optionally update deployment tag
    """
    setup_logging(verbose=False)
    src_dir = Path(source_directory).resolve()

    # 1) sanity
    if not src_dir.exists() or not src_dir.is_dir():
        click.echo(f"Source directory not found: {src_dir}", err=True)
        sys.exit(2)

    # 2) auth + workspace object
    credential = get_azure_credential()
    workspace = create_fabric_workspace_object(
        workspace_id=workspace_id,
        environment=environment,
        repo_directory=str(src_dir),
        credential=credential,
    )

    # 3) selection (full vs incremental)
    changed_items = None
    mode = (deploy_mode or "full").lower()

    if mode == "incremental":
        try:
            if delta.is_initial_deployment(src_dir, environment):
                click.echo("No previous deployment tag found → performing initial FULL deployment.")
                mode = "full"
            else:
                changed_items = delta.get_changed_files(src_dir, environment, source_dir=str(src_dir))
                if not changed_items:
                    click.echo("No changes detected.")
                    sys.exit(0)
        except RuntimeError as e:
            click.echo(f"Incremental detection failed, falling back to FULL: {e}", err=True)
            mode = "full"

    # 4) optional lakehouse processing
    if standardize_lakehouse_refs:
        lakehouse_core.apply(source_root=src_dir, dry_run=dry_run)

    # 5) deploy
    if mode == "incremental":
        if not changed_items:
            click.echo("No changed items detected for incremental deploy.")
            sys.exit(0)

        result = deploy_core.run_incremental(
            workspace=workspace,
            changed_items=changed_items,
            dry_run=dry_run,
        )

    elif mode == "full":
        result = deploy_core.run_full(workspace=workspace, dry_run=dry_run)

    else:
        click.echo(f"Invalid deploy mode: {mode!r}. Must be 'full' or 'incremental'.", err=True)
        sys.exit(1)

    # 6) optional tag update
    if update_deployment_tag:
        try:
            if dry_run:
                click.echo("Dry run: would update deployment tag at HEAD")
            else:
                delta.update_deployment_tag(src_dir, environment)
        except RuntimeError as e:
            click.echo(f"Warning: failed to update deployment tag: {e}", err=True)

    click.echo(result.message or ("Dry run completed." if dry_run else "Deployment completed."))
    sys.exit(0)
