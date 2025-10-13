"""
Deployment configuration model
"""

from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum


class DeployMode(Enum):
    """Deployment mode options."""

    FULL = "full"
    INCREMENTAL = "incremental"


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

        if not self.workspace_id or not isinstance(self.workspace_id, str):
            raise ValueError("workspace_id must be a non-empty string")

        if not self.source_directory.exists():
            raise ValueError(f"Source directory does not exist: {self.source_directory}")

        if not isinstance(self.deploy_mode, DeployMode):
            try:
                self.deploy_mode = DeployMode(self.deploy_mode.lower())
            except Exception:
                raise ValueError(f"Invalid deploy mode: {self.deploy_mode}")

        self.environment = self.environment.lower()
