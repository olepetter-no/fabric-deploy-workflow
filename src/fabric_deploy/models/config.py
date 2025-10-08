"""
Deployment configuration model
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class DeploymentConfig:
    """Simple configuration for a Fabric deployment"""

    workspace_id: str
    source_directory: Path
    environment: str = "dev"
    dry_run: bool = False

    def __post_init__(self):
        """Ensure source_directory is a Path object"""
        if isinstance(self.source_directory, str):
            self.source_directory = Path(self.source_directory)

        # Resolve to absolute path
        self.source_directory = self.source_directory.resolve()
