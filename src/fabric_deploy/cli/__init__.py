"""
CLI module for fabric-deploy-workflow

Provides command-line interface for deployment operations.
"""

import click
import sys
from pathlib import Path
import logging

from ..core.deployer import FabricDeployer
from ..core.validator import FabricValidator
from ..models.config import DeploymentConfig, FABRIC_ITEM_TYPES
from ..utils.logging import setup_logging
from ..utils.auth import get_azure_credential


@click.group()
def cli() -> None:
    """Microsoft Fabric deployment CLI"""
    pass


@cli.command()
@click.option("--workspace-id", required=True, help="Microsoft Fabric workspace ID")
@click.option(
    "--source-dir",
    default="./fabric",
    help="Source directory containing Fabric artifacts (must live inside a git repo)",
)
@click.option("--environment", default="dev", help="Target environment")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def validate(workspace_id: str, source_dir: str, environment: str, verbose: bool) -> None:
    """Validate deployment configuration and artifacts"""
    setup_logging(verbose=verbose)
    try:
        config = DeploymentConfig(workspace_id=workspace_id, source_directory=Path(source_dir), environment=environment)

        validator = FabricValidator(config)
        is_valid = validator.validate()

        if is_valid:
            click.echo("✅ Validation passed")
            sys.exit(0)
        else:
            click.echo("❌ Validation failed")
            sys.exit(1)

    except Exception as e:
        click.echo(f"❌ Validation error: {e}")
        sys.exit(1)


@cli.command()
@click.option("--workspace-id", required=True, help="Microsoft Fabric workspace ID")
@click.option(
    "--source-dir",
    default="./fabric",
    help="Source directory containing Fabric artifacts (must live inside a git repo)",
)
@click.option("--environment", default="dev", help="Target environment")
@click.option("--dry-run", is_flag=True, help="Perform a dry run without making changes")
@click.option(
    "--deploy-mode",
    type=click.Choice(["full", "incremental", "auto"], case_sensitive=False),
    default="auto",
    help="Deployment mode: full (deploy all), incremental (deploy changes), auto (incremental for dev/staging, full for prod)",
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.option(
    "--standardize-lakehouse-refs", is_flag=True, help="Standardize lakehouse references in notebooks before deployment"
)
@click.option(
    "--fabric-items",
    multiple=True,
    type=click.Choice(FABRIC_ITEM_TYPES, case_sensitive=False),
    help=f"Fabric item types to deploy (default: all). Available: {', '.join(FABRIC_ITEM_TYPES)}",
)
def deploy(
    workspace_id: str,
    source_dir: str,
    environment: str,
    dry_run: bool,
    deploy_mode: str,
    standardize_lakehouse_refs: bool,
    verbose: bool,
    fabric_items: tuple[str],
) -> None:
    """Deploy artifacts to Microsoft Fabric"""
    setup_logging(verbose=verbose)
    try:
        config = DeploymentConfig(
            workspace_id=workspace_id,
            source_directory=Path(source_dir),
            environment=environment,
            dry_run=dry_run,
            deploy_mode=deploy_mode,
            standardize_lakehouse_refs=standardize_lakehouse_refs,
            fabric_item_types=list(fabric_items) if fabric_items else None,
        )

        credential = get_azure_credential()
        deployer = FabricDeployer(config, credential)
        result = deployer.deploy()

        if result.success:
            if dry_run:
                if result.deployed_items == -1:
                    click.echo(f"🔄 Dry run: Would perform full deployment ({result.deployment_mode} mode)")
                elif result.deployed_items > 0:
                    click.echo(
                        f"⚡ Dry run: Would deploy {result.deployed_items} items ({result.deployment_mode} mode)"
                    )
                else:
                    click.echo(f"📭 Dry run: No changes detected ({result.deployment_mode} mode)")
            else:
                mode_info = f" ({result.deployment_mode} mode"
                if result.deployed_items >= 0:
                    mode_info += f", {result.deployed_items} items"
                mode_info += ")"
                click.echo(f"✅ Artifacts deployed successfully{mode_info}")

            sys.exit(0)
        else:
            click.echo(f"❌ {'Dry run' if dry_run else 'Deployment'} failed: {result.error_message}")
            sys.exit(1)

    except Exception as e:
        click.echo(f"❌ Deployment error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli()
