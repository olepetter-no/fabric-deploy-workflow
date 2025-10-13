
from pathlib import Path
from dataclasses import dataclass
import logging

from fabric_cicd import (
    FabricWorkspace,
    publish_all_items,
    append_feature_flag,
    append_feature_flag
)

logger = logging.getLogger(__name__)

# You can move this to models/result.py later if you like
@dataclass
class DeploymentResult:
    success: bool
    deployed_items: int
    mode: str
    message: str = ""

def run_full(
        *,
        workspace:FabricWorkspace,
        dry_run: bool,
) -> DeploymentResult:
    if dry_run:
        msg = (
            f"🔄 Dry run: Would perform FULL deployment to env={workspace.environment} "
            f"workspace={workspace.id}"
        )
        logger.info(msg)
        return DeploymentResult(True, 0, "full", msg)
    
    logger.info(
        "📤 FULL deployment: publishing all items to env=%s workspace=%s",
        workspace.environment,
        workspace.id,
    )
    publish_all_items(workspace)
    return DeploymentResult(True, 0, "full", "Full deployment succeeded.")

def run_incremental(
        *,
        workspace:FabricWorkspace,
        changed_items:list[str],
        dry_run:bool
) -> DeploymentResult:
    
    append_feature_flag("enable_experimental_features")
    append_feature_flag("enable_items_to_include")

    if dry_run:
        msg = f"🔄 Dry run: Would deploy {len(changed_items)} item(s): {changed_items}"
        logger.info(msg)
        return DeploymentResult(True, len(changed_items), "incremental", msg)

    logger.info(
        "📤 INCREMENTAL deployment: %d item(s) to env=%s workspace=%s",
        len(changed_items),
        workspace.environment,
        workspace.id,
    )
    publish_all_items(workspace, items_to_include=changed_items)
    return DeploymentResult(True, len(changed_items), "incremental", "Incremental deployment succeeded.")