from pathlib import Path
import subprocess
import logging
from typing import List

logger = logging.getLogger(__name__)


class GitOperations:
    """Git helper for incremental deploys. Fails fast on git errors."""

    def __init__(self, repo_path: Path):
        self.repo_path = Path(repo_path)

    def get_deployment_tag(self, environment: str) -> str:
        return f"latestDeployed/{environment}"

    def tag_exists(self, tag: str) -> bool:
        cp = self._run(["git", "rev-parse", "--verify", f"refs/tags/{tag}"], capture_output=True, text=True)
        return cp.returncode == 0

    def get_changed_files_since_tag(self, tag: str, source_dir: str) -> List[str]:
        if not self.tag_exists(tag):
            raise RuntimeError(f"Tag not found: {tag}")

        logger.info("Checking for changed files since %s", tag)
        cp = self._run(["git", "diff", "--name-only", f"{tag}..HEAD", "--", source_dir], capture_output=True, text=True)
        files = [f for f in cp.stdout.splitlines() if f]
        logger.info("Found %d changed file(s)", len(files))
        return files

    def create_or_update_tag(self, tag: str, ref: str = "HEAD") -> bool:
        if self.tag_exists(tag):
            logger.info("Updating existing tag: %s", tag)
            self._run(["git", "tag", "-d", tag])
        else:
            logger.info("Creating new tag: %s", tag)

        self._run(["git", "tag", tag, ref])

        if not self.tag_exists(tag):
            raise RuntimeError(f"Failed to verify tag creation: {tag}")

        logger.info("Tag %s created at %s", tag, ref)
        return True

    def is_initial_deployment(self, environment: str) -> bool:
        return not self.tag_exists(self.get_deployment_tag(environment))

    def _run(self, args, *, capture_output=False, text=None) -> subprocess.CompletedProcess:
        try:
            cp = subprocess.run(
                args,
                cwd=self.repo_path,
                capture_output=capture_output,
                text=(text if text is not None else capture_output),
                check=False,
            )
        except Exception as e:
            raise RuntimeError(f"Git exec failed: {' '.join(args)} ({e})")

        if cp.returncode != 0:
            raise RuntimeError(f"Git failed ({cp.returncode}): {' '.join(args)}")
        return cp
