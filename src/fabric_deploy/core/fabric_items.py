# core/fabric_items.py
import json
from pathlib import PurePath, Path
from typing import Iterable, Optional, List, Set

# Single source of truth for supported Microsoft Fabric item types
SUPPORTED_ITEM_TYPES: Set[str] = {
    "DataPipeline",
    "Environment",
    "Notebook",
    "Report",
    "SemanticModel",
    "Lakehouse",
    "MirroredDatabase",
    "VariableLibrary",
    "CopyJob",
    "Eventhouse",
    "KQLDatabase",
    "KQLQueryset",
    "Reflex",
    "Eventstream",
    "Warehouse",
    "SQLDatabase",
    "KQLDashboard",
    "Dataflow",
}

ITEM_PLATFORM_TYPE = ".platform"
ITEM_DISPLAY_NAME = "displayName"


def _read_display_name(item_dir: Path) -> Optional[str]:
    platform_file = item_dir / ITEM_PLATFORM_TYPE
    try:
        with platform_file.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("metadata", {}).get(ITEM_DISPLAY_NAME)
    except (FileNotFoundError, json.JSONDecodeError):
        raise Exception(f"Platform file not found")


def _extract_item_id(path: str) -> Optional[str]:
    """
    Given a file path, return the Fabric item ID (e.g., 'foo.Notebook')
    if the path is part of a recognized Fabric item folder.
    """
    parts = PurePath(path).parts
    print(parts)
    # Ignore the last segment (usually the file name)
    for idx, segment in enumerate(parts[:-1]):
        if "." not in segment:
            continue
        name, _, item_type = segment.rpartition(".")
        if name and item_type in SUPPORTED_ITEM_TYPES:
            item_dir = Path(*parts[: idx + 1])  # path up to and including this segment
            display_name = _read_display_name(item_dir)
            return f"{display_name}.{item_type}"

    return None

def extract_changed_items(paths: Iterable[str]) -> List[str]:
    """
    Given a list of changed file paths,
    return unique Fabric item IDs (e.g., 'foo.Notebook', 'bar.DataPipeline').
    """
    found_items: Set[str] = set()

    for path in paths:
        item_id = _extract_item_id(path)
        if item_id:
            found_items.add(item_id)

    return sorted(found_items)
