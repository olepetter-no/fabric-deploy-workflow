"""
Deployment configuration model
"""

from dataclasses import dataclass
from pathlib import Path
from enum import Enum

# Global Fabric item type configuration
FABRIC_ITEM_TYPES = [
    "Notebook",
    "DataPipeline", 
    "Environment",
]

FABRIC_ITEM_EXTENSIONS = [ f".{item}" for item in FABRIC_ITEM_TYPES ]

class DeployMode(Enum):
    FULL = "full"
    INCREMENTAL = "incremental"
    AUTO = "auto"


@dataclass
class DeploymentConfig:
    """Simple configuration for a Fabric deployment"""

    workspace_id: str
    source_directory: Path
    environment: str = "dev"
    dry_run: bool = False
    deploy_mode: DeployMode = DeployMode.AUTO
    standardize_lakehouse_refs: bool = False

    def __post_init__(self):
        if isinstance(self.source_directory, str):
            self.source_directory = Path(self.source_directory)

        # Resolve to absolute path
        self.source_directory = self.source_directory.resolve()

        # Ensure deploy_mode is enum
        if isinstance(self.deploy_mode, str):
            self.deploy_mode = DeployMode(self.deploy_mode)

        # Auto mode logic: incremental for dev/staging, full for prod
        if self.deploy_mode == DeployMode.AUTO:
            if self.environment in ["dev", "staging"]:
                self.deploy_mode = DeployMode.INCREMENTAL
            else:
                self.deploy_mode = DeployMode.FULL
