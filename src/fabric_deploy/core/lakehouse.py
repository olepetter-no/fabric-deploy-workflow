import logging
import pathlib
import re

logger = logging.getLogger(__name__)


def apply(source_root: pathlib.Path) -> None:
    """
    Standardize lakehouse references in all notebooks under source_root.

    Replaces IDs, workspace IDs, and names with placeholders:
      - REPLACEME_LAKEHOUSE
      - REPLACEME_WORKSPACE_ID
      - REPLACEME_LAKEHOUSE_NAME
    """
    if not source_root.exists():
        logger.error(f"❌ Source directory does not exist: {source_root}")
        return

    logger.info(f"🔄 Standardizing lakehouse references in: {source_root}")

    patterns, scan_pattern = _get_patterns()

    for notebook_dir in source_root.rglob("*.Notebook"):
        if not notebook_dir.is_dir():
            continue
        _process_notebook_dir(notebook_dir, patterns, scan_pattern)

    logger.info("✅ Lakehouse standardization completed.")


def _process_notebook_dir(notebook_dir: pathlib.Path, patterns, scan_pattern) -> None:
    """Process all .py files in a given notebook directory."""
    for file_path in notebook_dir.glob("*.py"):
        try:
            if file_path.stat().st_size > 10 * 1024 * 1024:
                logger.warning(f"⚠️  Skipping large file: {file_path}")
                continue
            _process_file(file_path, patterns, scan_pattern)
        except Exception as e:
            logger.warning(f"⚠️  Could not process {file_path}: {e}")


def _process_file(file_path: pathlib.Path, patterns, scan_pattern) -> None:
    """Standardize a single notebook file if lakehouse references are found."""
    try:
        text = file_path.read_text(encoding="utf-8")
        if not scan_pattern.search(text):
            return

        new_text = text
        for pattern, replacement in patterns:
            new_text = pattern.sub(replacement, new_text)

        if new_text != text:
            file_path.write_text(new_text, encoding="utf-8")
            logger.debug(f"📝 Standardized: {file_path.name}")

    except Exception as e:
        logger.warning(f"⚠️  Error processing {file_path}: {e}")


def _get_patterns():
    """Precompiled regex patterns for replacing lakehouse references."""
    patterns = [
        (re.compile(r'"default_lakehouse":\s*"([0-9a-fA-F-]{36})"'),
         '"default_lakehouse": "REPLACEME_LAKEHOUSE"'),
        (re.compile(r'"default_lakehouse_name":\s*"[^"]+"'),
         '"default_lakehouse_name": "REPLACEME_LAKEHOUSE_NAME"'),
        (re.compile(r'"default_lakehouse_workspace_id":\s*"([0-9a-fA-F-]{36})"'),
         '"default_lakehouse_workspace_id": "REPLACEME_WORKSPACE_ID"'),
        (re.compile(r'"lakehouse_id":\s*"([0-9a-fA-F-]{36})"'),
         '"lakehouse_id": "REPLACEME_LAKEHOUSE"'),
    ]
    scan_pattern = re.compile(r'"(default_)?lakehouse(_name|_workspace_id|_id)?":\s*"', re.IGNORECASE)
    return patterns, scan_pattern
