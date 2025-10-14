"""
Deployment configuration model
"""

import re

from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum


class DeployMode(Enum):
    """Deployment mode options."""

    FULL = "full"
    INCREMENTAL = "incremental"


_GUID_RE = re.compile(r"^[0-9a-fA-F]{8}-(?:[0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}$")


@dataclass
class DeploymentConfig:
    """
    Configuration object for Fabric deployment.

    Represents the resolved deployment settings for a single run.
    Typically constructed by the CLI layer and passed into core logic.
    """

    workspace_id: str
    source_directory: Path
    environment: str = "dev"
    dry_run: bool = False
    deploy_mode: DeployMode = DeployMode.FULL
    standardize_lakehouse_refs: bool = False
    fabric_item_types: list[str] = field(default_factory=list)
    update_deployment_tag: bool = True  # singular for clarity — matches function name

    def __post_init__(self):
        if not isinstance(self.source_directory, Path):
            self.source_directory = Path(self.source_directory)

        if not isinstance(self.workspace_id, str) or not _GUID_RE.match(self.workspace_id):
            raise ValueError("workspace_id must be a valid GUID (xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)")

        if not self.source_directory.exists() or not self.source_directory.is_dir():
            raise ValueError(f"Source directory does not exist or is not a directory: {self.source_directory}")

        if not isinstance(self.deploy_mode, DeployMode):
            try:
                self.deploy_mode = DeployMode(self.deploy_mode.lower())
            except Exception:
                raise ValueError(f"Invalid deploy mode: {self.deploy_mode}")

        self.environment = self.environment.lower()
