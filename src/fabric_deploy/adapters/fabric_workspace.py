from fabric_cicd import FabricWorkspace
from typing import Optional

def create_fabric_workspace_object(
    workspace_id: str, environment: str, repo_directry: str, item_type_in_scope: Optional[list[str]] = None, credentials = None
) -> "FabricWorkspace":
    """Creates and configure FabricWorkspace object"""
    return FabricWorkspace(
        workspace_id=workspace_id,
        environment=environment,
        repository_directory=repo_directry,
        item_type_in_scope=item_type_in_scope,
        credentials=credentials
    )
