import pathlib
import re
import logging


class LakehouseStandardizer:
    """Standardizes lakehouse references in Fabric notebooks for environment-specific deployment."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Pre-compile patterns for better performance
        self._compiled_patterns = [
            (
                re.compile(
                    r'"default_lakehouse":\s*"([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})"'
                ),
                '"default_lakehouse": "REPLACEME_LAKEHOUSE"',
            ),
            (
                re.compile(r'"default_lakehouse_name":\s*"([^"]+)"'),
                '"default_lakehouse_name": "REPLACEME_LAKEHOUSE_NAME"',
            ),
            (
                re.compile(
                    r'"default_lakehouse_workspace_id":\s*"([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})"'
                ),
                '"default_lakehouse_workspace_id": "REPLACEME_WORKSPACE_ID"',
            ),
            (
                re.compile(
                    r'"lakehouse_id":\s*"([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})"'
                ),
                '"lakehouse_id": "REPLACEME_LAKEHOUSE"',
            ),
        ]

        # Pre-compile a quick check pattern to avoid processing files without lakehouse refs
        self._has_lakehouse_pattern = re.compile(
            r'"(default_)?lakehouse(_name|_workspace_id|_id)?":\s*"', re.IGNORECASE
        )

    def standardize_notebooks(self, source_directory: pathlib.Path) -> bool:
        if not source_directory.exists():
            self.logger.error(f"❌ Source directory does not exist: {source_directory}")
            return False

        self.logger.info(f"🔄 Standardizing lakehouse references in: {source_directory}")

        try:
            for notebook_dir in source_directory.rglob("*.Notebook"):
                if not notebook_dir.is_dir():
                    continue

                self._process_notebook_directory(notebook_dir)

            self.logger.info("✅ Lakehouse standardization complete")
            return True

        except Exception as e:
            self.logger.error(f"❌ Lakehouse standardization failed: {e}")
            return False

    def _process_notebook_directory(self, notebook_dir: pathlib.Path):
        for file_path in notebook_dir.glob("*.py"):
            try:
                # Quick file size check to avoid processing huge files
                file_size = file_path.stat().st_size
                if file_size > 10 * 1024 * 1024:  # 10MB limit
                    self.logger.warning(f"⚠️  Skipping large file: {file_path} ({file_size / (1024*1024):.1f}MB)")
                    continue

                self._process_single_file(file_path)

            except Exception as e:
                self.logger.warning(f"⚠️  Could not process {file_path}: {e}")

    def _process_single_file(self, file_path: pathlib.Path):
        try:
            content = file_path.read_text(encoding="utf-8")

            # Quick check: does this file even contain lakehouse references?
            if not self._has_lakehouse_pattern.search(content):
                return

            # Apply standardization patterns
            modified_content = content
            for pattern, replacement in self._compiled_patterns:
                modified_content = pattern.sub(replacement, modified_content)

            # Only write if content actually changed
            if modified_content != content:
                file_path.write_text(modified_content, encoding="utf-8")
                self.logger.debug(f"📝 Standardized: {file_path.name}")

        except Exception as e:
            self.logger.warning(f"⚠️  Error processing {file_path}: {e}")
