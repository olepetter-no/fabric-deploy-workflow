"""
Git operations for tracking deployment state
"""

import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


class GitOperations:
    """Handle git operations for incremental deployments"""

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path

    def get_deployment_tag(self, environment: str) -> str:
        return f"latestDeployed/{environment}"

    def tag_exists(self, tag_name: str) -> bool:
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--verify", f"refs/tags/{tag_name}"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
            )
            return result.returncode == 0
        except Exception as e:
            logger.warning(f"Error checking tag existence: {e}")
            return False

    def get_changed_files_since_tag(self, tag_name: str, source_directory: str) -> list[str]:
        """
        Get list of files changed in source directory since a specific tag.

        This method focuses only on changes within the source directory containing
        Fabric artifacts, ignoring changes to documentation, workflows, or other
        non-deployment-relevant files.

        Args:
            tag_name: Git tag to compare against
            source_directory: Path to source directory containing Fabric artifacts

        Returns:
            List of changed file paths relative to repository root
        """
        try:
            # Get files changed between tag and current HEAD, filtered to source directory
            result = subprocess.run(
                ["git", "diff", "--name-only", f"{tag_name}..HEAD", "--", source_directory],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            changed_files = [f.strip() for f in result.stdout.split("\n") if f.strip()]
            logger.info(f"Found {len(changed_files)} changed files in {source_directory} since {tag_name}")
            logger.debug(f"Changed files: {changed_files}")
            return changed_files
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to get changed files since tag {tag_name}: {e}")
            return []

    def create_or_update_tag(self, tag_name: str, ref: str = "HEAD") -> bool:
        try:
            logger.info(f"🏷️  Creating/updating tag '{tag_name}' in repository: {self.repo_path}")

            # Delete tag locally if it exists
            if self.tag_exists(tag_name):
                logger.info(f"🗑️  Deleting existing local tag: {tag_name}")
                subprocess.run(
                    ["git", "tag", "-d", tag_name],
                    cwd=self.repo_path,
                    capture_output=True,
                    check=True,
                )

            # Create new tag locally
            logger.info(f"✨ Creating new local tag: {tag_name} at {ref}")
            result = subprocess.run(
                ["git", "tag", tag_name, ref],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )

            # Verify local tag was created
            if self.tag_exists(tag_name):
                logger.info(f"✅ Successfully created local tag: {tag_name}")

                # Show tag details
                tag_info_result = subprocess.run(
                    ["git", "show", "--no-patch", "--format=%H %s", tag_name],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                )
                if tag_info_result.returncode == 0:
                    logger.info(f"📋 Tag details: {tag_info_result.stdout.strip()}")

                logger.info(
                    f"� Local tag '{tag_name}' created successfully. Push to remote will be handled by workflow."
                )
                return True

            else:
                logger.error(f"❌ Tag creation appeared to succeed but tag not found: {tag_name}")
                return False

        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Error creating tag {tag_name}: {e}")
            logger.error(f"   stdout: {e.stdout}")
            logger.error(f"   stderr: {e.stderr}")
            return False

    def is_initial_deployment(self, environment: str) -> bool:
        tag_name = self.get_deployment_tag(environment)
        return not self.tag_exists(tag_name)
