"""
core.validate
-------------
Performs lightweight validation of deployment configuration and source artifacts.
"""

import logging
from pathlib import Path
from ..models.config import DeploymentConfig
from ..adapters.git_ops import GitOperations

logger = logging.getLogger(__name__)


def run(workspace_id: str, source_directory: Path, environment: str) -> bool:
    """
    Validate that the deployment configuration and source directory are valid.
    Returns True if validation succeeds, False otherwise.
    """
    logger.info("🔍 Starting validation")

    try:
        cfg = DeploymentConfig(
            workspace_id=workspace_id,
            source_directory=source_directory,
            environment=environment,
        )

        if not GitOperations.is_within_repo(source_directory):
            raise ValueError(f"No Git repository found for source directory: '{source_directory}'")

        logger.info("✅ Validation succeeded")
        return True

    except Exception as e:
        logger.warning(f"❌ Validation failed: {e}")
        return False


def _check_source_structure(source_dir: Path):
    if not source_dir.exists():
        raise ValueError(f"Source directory not found: {source_dir}")
