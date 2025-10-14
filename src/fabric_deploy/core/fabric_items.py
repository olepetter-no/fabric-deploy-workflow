# core/fabric_items.py
from pathlib import PurePath
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


def extract_item_id(path: str) -> Optional[str]:
    """
    Given a file path, return the Fabric item ID (e.g., 'foo.Notebook')
    if the path is part of a recognized Fabric item folder.
    """
    parts = PurePath(path).parts

    # Ignore the last segment (usually the file name)
    for segment in parts[:-1]:
        if "." not in segment:
            continue
        name, _, item_type = segment.rpartition(".")
        if name and item_type in SUPPORTED_ITEM_TYPES:
            return f"{name}.{item_type}"

    return None


def extract_changed_items(paths: Iterable[str]) -> List[str]:
    """
    Given a list of changed file paths,
    return unique Fabric item IDs (e.g., 'foo.Notebook', 'bar.DataPipeline').
    """
    found_items: Set[str] = set()

    for path in paths:
        item_id = extract_item_id(path)
        if item_id:
            found_items.add(item_id)

    return sorted(found_items)
