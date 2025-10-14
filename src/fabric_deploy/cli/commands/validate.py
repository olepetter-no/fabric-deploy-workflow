import sys
from pathlib import Path

import click

from ...core import validate as validate_core
from ...utils.logging import setup_logging


@click.command(help="Validate deployment configuration and artifacts.")
@click.option("--workspace-id", "workspace_id", required=True, help="Microsoft Fabric workspace ID")
@click.option(
    "--source-directory",
    default="./fabric",
    show_default=True,
    help="Directory containing Fabric artifacts (must be in a git repo)",
)
@click.option("--environment", required=True, help="Target environment (dev|staging|prod)")
@click.option(
    "--verbose",
    is_flag=True,
    default=False,
    help="Enable verbose (debug-level) output.",
)
def cmd(workspace_id, source_directory, environment, verbose):
    """Thin wrapper around core.validate.run()."""
    setup_logging(verbose=verbose)

    try:
        ok = validate_core.run(
            workspace_id=workspace_id,
            source_directory=Path(source_directory),
            environment=environment,
        )
        click.echo("✅ Validation passed" if ok else "❌ Validation failed")
        sys.exit(0 if ok else 1)

    except Exception as e:
        click.echo(f"❌ Validation error: {e}", err=True)
        sys.exit(1)
