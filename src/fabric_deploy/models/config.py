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
    "Report",
    "SemanticModel",
    "Lakehouse",
    "Warehouse",
    "KQLDatabase",
]

FABRIC_ITEM_EXTENSIONS = [f".{item}" for item in FABRIC_ITEM_TYPES]


class DeployMode(Enum):
    FULL = "full"
    INCREMENTAL = "incremental"


@dataclass
class DeploymentConfig:
    """Simple configuration for a Fabric deployment"""

    workspace_id: str
    source_directory: Path
    environment: str = "dev"
    dry_run: bool = False
    deploy_mode: DeployMode = DeployMode.FULL
    standardize_lakehouse_refs: bool = False
    fabric_item_types: list[str] = None  # Subset of FABRIC_ITEM_TYPES to deploy
    update_deployment_tags: bool = True  # Create and update deployment tags

    def __post_init__(self):
        if isinstance(self.source_directory, str):
            self.source_directory = Path(self.source_directory)

        # Resolve to absolute path
        self.source_directory = self.source_directory.resolve()

        # Ensure deploy_mode is enum
        if isinstance(self.deploy_mode, str):
            self.deploy_mode = DeployMode(self.deploy_mode)

        # Set default fabric item types if not specified
        if self.fabric_item_types is None:
            self.fabric_item_types = FABRIC_ITEM_TYPES.copy()
        else:
            # Validate that specified types are supported
            invalid_types = [t for t in self.fabric_item_types if t not in FABRIC_ITEM_TYPES]
            if invalid_types:
                raise ValueError(
                    f"Unsupported Fabric item types: {invalid_types}. Supported types: {FABRIC_ITEM_TYPES}"
                )

        # Generate extensions list from selected types
        self.fabric_item_extensions = [f".{item}" for item in self.fabric_item_types]
