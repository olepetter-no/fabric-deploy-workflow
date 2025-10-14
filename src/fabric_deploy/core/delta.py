from pathlib import Path

from ..adapters.git_ops import GitOperations


def _git(repo_root: Path) -> GitOperations:
    return GitOperations(repo_root)


def is_initial_deployment(repo_root: Path, environment: str) -> bool:
    return _git(repo_root).is_initial_deployment(environment)


def get_changed_files(repo_root: Path, environment: str, *, source_dir: str) -> list[str]:
    """Returns changed files within source_dir since last deployment tag."""
    g = _git(repo_root)
    tag = g.get_deployment_tag(environment)
    return g.get_changed_files_since_tag(tag, source_dir=source_dir)


def update_deployment_tag(repo_root: Path, environment: str) -> None:
    g = _git(repo_root)
    tag = g.get_deployment_tag(environment)
    g.create_or_update_tag(tag, ref="HEAD")
