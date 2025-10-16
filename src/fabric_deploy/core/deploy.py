from pathlib import Path
from dataclasses import dataclass
import logging

from fabric_cicd import (
    FabricWorkspace,
    publish_all_items,
    append_feature_flag,
    append_feature_flag,
    unpublish_all_orphan_items,
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
    workspace: FabricWorkspace,
    dry_run: bool,
) -> DeploymentResult:
    if dry_run:
        msg = f"[Dry run]: 🔄 Would perform FULL deployment"
        logger.info(msg)
        return DeploymentResult(True, 0, "full", msg)

    logger.info(
        "📤 FULL deployment: publishing all items to env=%s workspace=%s",
        workspace.environment,
        workspace.workspace_id,
    )
    try:
        publish_all_items(workspace)
        return DeploymentResult(True, 0, "full", "Full deployment succeeded.")
    except Exception as exc:
        logger.exception("Full deployment failed.")
        return DeploymentResult(False, 0, "full", f"Full deployment failed: {exc}")


def run_incremental(*, workspace: FabricWorkspace, changed_items: list[str], dry_run: bool) -> DeploymentResult:

    append_feature_flag("enable_experimental_features")
    append_feature_flag("enable_items_to_include")

    if dry_run:
        msg = f"[Dry run]: 🔄 Would deploy {len(changed_items)} item(s): {changed_items}"
        logger.info(msg)
        return DeploymentResult(True, len(changed_items), "incremental", msg)

    logger.info(
        "📤 INCREMENTAL deployment: %d item(s) to env=%s workspace=%s",
        len(changed_items),
        workspace.environment,
        workspace.workspace_id,
    )

    logger.debug(f"Changed items: {changed_items}")

    try:
        publish_all_items(workspace, items_to_include=list(changed_items))
        return DeploymentResult(True, len(changed_items), "incremental", "Incremental deployment succeeded.")
    except Exception as exc:
        logger.exception("Incremental deployment failed.")
        return DeploymentResult(False, len(changed_items), "incremental", f"Incremental deployment failed: {exc}")


def run_unpublish_orphans(*, workspace: FabricWorkspace, dry_run: bool, item_name_exclude_regex: str = "^$"):
    if dry_run:
        msg = f"[Dry run]: 🔄 Would unpublish orphan items"
        return DeploymentResult(True, 0, "unpublish", msg)

    logger.info(
        "🧹 Unpublishing orphan items in env=%s workspace=%s",
        workspace.environment,
        workspace.workspace_id,
    )

    try:
        unpublish_all_orphan_items(workspace, item_name_exclude_regex=item_name_exclude_regex)
        return DeploymentResult(True, 0, "unpublish", "Unpublish orphans succeeded.")
    except Exception as exc:
        logger.error("Unpublish orphans failed.")
        return DeploymentResult(False, 0, "unpublish", f"Unpublish orphans failed: {exc}")
