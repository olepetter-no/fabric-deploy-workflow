"""
Microsoft Fabric Deployer

Handles the deployment of artifacts to Microsoft Fabric workspaces using fabric-cicd.
"""

import logging
from typing import List, Optional
from dataclasses import dataclass

from azure.identity import DefaultAzureCredential

from ..models.config import DeploymentConfig


@dataclass
class DeploymentResult:
    """Result of a deployment operation"""

    success: bool
    error_message: Optional[str] = None


class FabricDeployer:
    """Simple deployer class for Microsoft Fabric artifacts using fabric-cicd"""

    def __init__(self, config: DeploymentConfig, credential: DefaultAzureCredential):
        """
        Initialize the Fabric deployer

        Args:
            config: Deployment configuration
            credential: Azure credential for authentication
        """
        self.config = config
        self.credential = credential
        self.logger = logging.getLogger(__name__)

    def deploy(self) -> DeploymentResult:
        """
        Deploy artifacts to Microsoft Fabric using fabric-cicd

        Returns:
            DeploymentResult with success status and details
        """
        try:
            self.logger.info(f"Starting deployment to workspace {self.config.workspace_id}")

            if self.config.dry_run:
                self.logger.info("Performing dry run - no actual changes will be made")

            # Import fabric-cicd components
            from fabric_cicd import FabricWorkspace, publish_all_items, unpublish_all_orphan_items

            # Initialize the FabricWorkspace object - same for both dry-run and actual
            target_workspace = FabricWorkspace(
                workspace_id=self.config.workspace_id,
                environment=self.config.environment,
                repository_directory=str(self.config.source_directory),
                # Include common Fabric item types - fabric-cicd will handle what exists
                item_type_in_scope=[
                    "Notebook",
                    "DataPipeline",
                    "Environment",
                    "Report",
                    "SemanticModel",
                    "Lakehouse",
                    "Warehouse",
                    "KQLDatabase",
                ],
            )

            if self.config.dry_run:
                # For dry-run, we could potentially call fabric-cicd with dry-run parameters
                # if it supports them, or just validate the workspace setup
                self.logger.info("Dry run: Validated workspace configuration and source directory")
                self.logger.info("Dry run: Would publish all items to Fabric workspace")
                self.logger.info("Dry run: Would remove orphaned items from workspace")
                action = "would be deployed"
            else:
                # Actual deployment
                self.logger.info("Publishing all items to Fabric workspace")
                publish_all_items(target_workspace)

                # Clean up orphaned items
                self.logger.info("Removing orphaned items from workspace")
                unpublish_all_orphan_items(target_workspace)
                action = "deployed"

            self.logger.info(f"Deployment completed successfully - artifacts {action}")
            return DeploymentResult(success=True)

        except ImportError as e:
            error_msg = f"fabric-cicd library not available: {e}"
            self.logger.error(error_msg)
            return DeploymentResult(success=False, error_message=error_msg)
        except Exception as e:
            error_msg = f"Deployment failed: {e}"
            self.logger.error(error_msg)
            return DeploymentResult(success=False, error_message=error_msg)
