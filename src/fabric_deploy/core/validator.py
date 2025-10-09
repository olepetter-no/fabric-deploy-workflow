"""
Validation module for Microsoft Fabric deployments

Validates basic configuration and directory structure before deployment.
"""

import logging
import re

from ..models.config import DeploymentConfig


class FabricValidator:
    """Simple validator for Fabric deployment configuration"""

    def __init__(self, config: DeploymentConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def validate(self) -> bool:
        """Returns True if validation passes, False otherwise"""

        self.logger.info("Starting basic validation")

        # Reset errors and warnings
        self.errors.clear()
        self.warnings.clear()

        # Run validation checks
        self._validate_configuration()
        self._validate_source_directory()
        self._validate_workspace_id()

        # Report results
        self._report_results()

        success = len(self.errors) == 0
        self.logger.info(f"Validation {'passed' if success else 'failed'}")
        return success

    def _report_results(self) -> None:
        """Report validation errors and warnings"""
        if self.errors:
            self.logger.error(f"Validation failed with {len(self.errors)} errors:")
            for error in self.errors:
                self.logger.error(f"  - {error}")

        if self.warnings:
            self.logger.warning(f"Validation completed with {len(self.warnings)} warnings:")
            for warning in self.warnings:
                self.logger.warning(f"  - {warning}")

    def _validate_configuration(self) -> None:
        """Validate the deployment configuration"""
        if not self.config.workspace_id:
            self.errors.append("Workspace ID is required")

        if not self.config.source_directory:
            self.errors.append("Source directory is required")

        if self.config.environment not in ["dev", "staging", "prod"]:
            self.warnings.append(f"Non-standard environment: {self.config.environment}")

    def _validate_source_directory(self) -> None:
        """Validate the source directory exists and is accessible"""
        if not self.config.source_directory.exists():
            self.errors.append(f"Source directory does not exist: {self.config.source_directory}")
            return

        if not self.config.source_directory.is_dir():
            self.errors.append(f"Source path is not a directory: {self.config.source_directory}")
            return

    def _validate_workspace_id(self) -> None:
        """Validate the workspace ID format"""
        workspace_id = self.config.workspace_id

        # Basic format validation (Fabric workspace IDs are GUIDs)
        if len(workspace_id) != 36:
            self.warnings.append("Workspace ID does not appear to be a standard GUID format")
            return

        # Check for GUID pattern
        guid_pattern = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")
        if not guid_pattern.match(workspace_id):
            self.warnings.append("Workspace ID does not match expected GUID format")
