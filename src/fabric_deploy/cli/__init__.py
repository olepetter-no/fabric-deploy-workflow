"""
CLI module for fabric-deploy-workflow

Provides command-line interface for deployment operations.
"""

import click
import sys
import logging
from pathlib import Path
from typing import Optional

from ..core.deployer import FabricDeployer
from ..core.validator import FabricValidator
from ..models.config import DeploymentConfig
from ..utils.logging import setup_logging
from ..utils.auth import get_azure_credential


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.option("--log-file", help="Log file path")
def cli(verbose: bool, log_file: Optional[str]) -> None:
    """Microsoft Fabric deployment CLI"""
    setup_logging(verbose=verbose, log_file=log_file)


@cli.command()
@click.option("--workspace-id", required=True, help="Microsoft Fabric workspace ID")
@click.option("--source-dir", default="./fabric", help="Source directory containing Fabric artifacts")
@click.option("--environment", default="dev", help="Target environment")
def validate(workspace_id: str, source_dir: str, environment: str) -> None:
    """Validate deployment configuration and artifacts"""
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
@click.option("--source-dir", default="./fabric", help="Source directory containing Fabric artifacts")
@click.option("--environment", default="dev", help="Target environment")
@click.option("--dry-run", is_flag=True, help="Perform a dry run without making changes")
def deploy(workspace_id: str, source_dir: str, environment: str, dry_run: bool) -> None:
    """Deploy artifacts to Microsoft Fabric"""
    try:
        config = DeploymentConfig(
            workspace_id=workspace_id, source_directory=Path(source_dir), environment=environment, dry_run=dry_run
        )

        credential = get_azure_credential()
        deployer = FabricDeployer(config, credential)

        result = deployer.deploy()

        if result.success:
            action = "would be deployed" if dry_run else "deployed"
            click.echo(f"✅ Artifacts {action} successfully")
            sys.exit(0)
        else:
            click.echo(f"❌ Deployment failed: {result.error_message}")
            sys.exit(1)

    except Exception as e:
        click.echo(f"❌ Deployment error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli()
