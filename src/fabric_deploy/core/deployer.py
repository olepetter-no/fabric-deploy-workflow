"""
Microsoft Fabric Deployer

Handles the deployment of artifacts to Microsoft Fabric workspaces using fabric-cicd.
"""

import logging
from typing import Optional
from dataclasses import dataclass
from pathlib import Path

from azure.identity import DefaultAzureCredential
from fabric_cicd import (
    FabricWorkspace,
    publish_all_items, 
    append_feature_flag,
    unpublish_all_orphan_items
)

from ..models.config import DeploymentConfig, DeployMode, FABRIC_ITEM_EXTENSIONS
from ..utils.git_operations import GitOperations
from ..utils.lakehouse_processor import LakehouseStandardizer


@dataclass
class DeploymentResult:
    success: bool
    error_message: Optional[str] = None
    deployed_items: int = 0
    deployment_mode: str = "unknown"


class FabricDeployer:

    def __init__(self, config: DeploymentConfig, credential: DefaultAzureCredential):
        """
        Args:
            config: Deployment configuration
            credential: Azure credential for authentication
        """
        self.config = config
        self.credential = credential
        self.git_ops = GitOperations(self._find_git_root())
        self.lakehouse_standardizer = LakehouseStandardizer()

    def _find_git_root(self) -> Path:
        """Find the git root directory - raises error if not found"""
        current = self.config.source_directory.resolve()
        while current != current.parent:
            if (current / ".git").exists():
                return current
            current = current.parent
        
        raise RuntimeError(
            f"❌ No git repository found!\n"
            f"   Searched from: {self.config.source_directory}\n"
            f"   Up to: {current}\n"
            f"   \n"
            f"   fabric-deploy requires a git repository for:\n"
            f"   • Incremental deployment change detection\n"
            f"   • Deployment history tracking\n"
            f"   • Tag management\n"
        )

    def _map_changed_files_to_items(self, changed_files: list[str]) -> list[str]:
        """Map changed files to Fabric item names by finding .Notebook/.DataPipeline directories"""
        items = []
        source_dir_name = self.config.source_directory.name
        
        # Fabric item types that have directory extensions
        FABRIC_EXTENSIONS = [".Notebook", ".DataPipeline", ".Environment", ".Report", 
                            ".SemanticModel", ".Lakehouse", ".Warehouse", ".KQLDatabase"]
        
        for file_path in changed_files:
            path_obj = Path(file_path)
            
            try:
                source_index = path_obj.parts.index(source_dir_name)
                remaining_parts = path_obj.parts[source_index + 1:]
                
                # Find the first directory that ends with a Fabric extension
                for part in remaining_parts:
                    if any(part.endswith(ext) for ext in FABRIC_EXTENSIONS):
                        if part not in items:
                            items.append(part)
                            self.logger.info(f"Mapped changed file to item: {part}")
                        break  # Found the item, stop searching
                        
            except ValueError:
                self.logger.debug(f"Skipping file outside source directory: {file_path}")
                continue
        
        return items

    def _create_fabric_workspace_object(self) -> 'FabricWorkspace':
        """Creates and configure FabricWorkspace object"""        
        return FabricWorkspace(
            workspace_id=self.config.workspace_id,
            environment=self.config.environment,
            repository_directory=str(self.config.source_directory),
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
    
    def _handle_full_deployment(self, target_workspace: 'FabricWorkspace') -> int:       
        self.logger.info("📤 Publishing all items to Fabric workspace (full deployment)...")
        if self.config.dry_run:
            self.logger.info("🔄 Dry run: Would perform FULL deployment of all items")
            return -1 
        
        publish_all_items(target_workspace)
        return -1  # Indicate full deployment

    def _handle_incremental_deployment(self, target_workspace: 'FabricWorkspace') -> int:       
        tag_name = self.git_ops.get_deployment_tag(self.config.environment)
        source_files = self.git_ops.get_changed_files_since_tag(tag_name, str(self.config.source_directory))
        changed_items = self._map_changed_files_to_items(source_files)
        if changed_items:           
            # Enable feature flags for incremental deployment
            append_feature_flag("enable_experimental_features")
            append_feature_flag("enable_items_to_include")

            if self.config.dry_run:
                self.logger.info(f"🔄 Dry run: Would deploy {len(changed_items)} items: {changed_items}")
                return len(changed_items)
            
            self.logger.info(f"📤 Publishing {len(changed_items)} changed items to Fabric workspace...")
            publish_all_items(target_workspace, items_to_include=changed_items)
            return len(changed_items)
        else:
            self.logger.info("📭 No items to publish (no changes detected)")
            return 0

    def _cleanup_and_tag_deployment(self, deployed_items: int, effective_mode: DeployMode, target_workspace) -> None:            
        # Clean up orphaned items from workspace
        if self.config.dry_run:
            self.logger.info("🔄 Dry run: Would clean up orphaned items from workspace")
        else:
            self.logger.info("🧹 Removing orphaned items from workspace")
            unpublish_all_orphan_items(target_workspace)

        # Update deployment tag
        if deployed_items != 0 or effective_mode == DeployMode.FULL:
            tag_name = self.git_ops.get_deployment_tag(self.config.environment)

            if self.config.dry_run:
                self.logger.info("🔄 Dry run: Would update deployment tag")
                return
            else:
                if self.git_ops.create_or_update_tag(tag_name):
                    self.logger.info(f"✅ Updated deployment tag: {tag_name}")
                else:
                    self.logger.warning(f"⚠️  Failed to update deployment tag: {tag_name}")

    @property
    def logger(self):
        """Get logger with current configuration (called after setup_logging)"""
        return logging.getLogger(__name__)

    def deploy(self) -> DeploymentResult:
        try:
            self.logger.info(f"Starting {self.config.deploy_mode.value} deployment to workspace {self.config.workspace_id}")

            if self.config.dry_run:
                self.logger.info("Performing dry run - no actual changes will be made")

            # Standardize lakehouse references if enabled
            if self.config.standardize_lakehouse_refs:
                self.logger.info("🔧 Standardizing lakehouse references in notebooks...")
                if not self.lakehouse_standardizer.standardize_notebooks(self.config.source_directory):
                    self.logger.warning("⚠️  Lakehouse standardization completed with warnings")
                    # Continue deployment even if standardization has warnings

            # Check if this is initial deployment
            is_initial = self.git_ops.is_initial_deployment(self.config.environment)
            
            # Determine effective deployment mode
            effective_mode = DeployMode.FULL if is_initial else self.config.deploy_mode
            
            if is_initial:
                self.logger.info("Initial deployment detected - using full deployment mode")

            # Create workspace for actual deployment
            target_workspace = self._create_fabric_workspace_object()
            
            # Perform deployment based on mode
            if effective_mode == DeployMode.FULL:
                deployed_items = self._handle_full_deployment(target_workspace)
            else:
                deployed_items = self._handle_incremental_deployment(target_workspace)

            # Clean up and update tags
            self._cleanup_and_tag_deployment(deployed_items, effective_mode, target_workspace)
            action = "deployed"

            self.logger.info(f"Deployment completed successfully - artifacts {action}")
            return DeploymentResult(
                success=True, 
                deployed_items=deployed_items,
                deployment_mode=effective_mode.value
            )

        except Exception as e:
            error_msg = f"Deployment failed: {e}"
            self.logger.error(error_msg)
            return DeploymentResult(success=False, error_message=error_msg)
