"""
Microsoft Fabric Deployment Workflow

A Python package for deploying Microsoft Fabric solutions via GitHub Actions.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .core.deployer import FabricDeployer
from .core.validator import FabricValidator
from .models.config import DeploymentConfig

__all__ = [
    "FabricDeployer",
    "FabricValidator",
    "DeploymentConfig",
]
