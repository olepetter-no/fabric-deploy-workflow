from pathlib import Path
import subprocess
import logging
from typing import List

logger = logging.getLogger(__name__)


class GitOperations:
    """Git helper for incremental deploys. Fails fast on git errors."""

    def __init__(self, repo_path: Path):
        self.repo_path = Path(repo_path)

    @staticmethod
    def is_within_repo(path: str | Path) -> bool:
        try:
            subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                cwd=Path(path).resolve(),
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
            )
            return True
        except subprocess.CalledProcessError as e:
            logging.error(f"Git command failed: {e.stderr.strip() or 'unknown error'}")
            if e.returncode == 128:
                return False
            raise RuntimeError(f"Git error (code {e.returncode}): {e.stderr.strip() or 'unknown error'}") from e
        except Exception as e:
            raise RuntimeError(f"Unexpected error while checking git repo: {e}") from e

    def _get_repo_root(self, path: str | Path) -> Path:
        """Return the absolute path to the root of the current Git repository."""
        try:
            p = Path(path).resolve()
            start = p if p.is_dir() else p.parent
            root = subprocess.check_output(
                ["git", "rev-parse", "--show-toplevel"],
                text=True,
                cwd=start
            ).strip()
            return Path(root)
        except subprocess.CalledProcessError:
            raise RuntimeError("Not inside a Git repository.")
    
    def get_deployment_tag(self, environment: str) -> str:
        return f"latestDeployed/{environment}"

    def tag_exists(self, tag: str) -> bool:
        cp = self._run(
            ["git", "rev-parse", "--verify", f"refs/tags/{tag}"],
            capture_output=True,
            text=True,
            allow_fail=True,  # allow exit 128
        )
        return cp.returncode == 0

    def get_changed_files_since_tag(self, tag: str, source_dir: str) -> List[str]:
        if not self.tag_exists(tag):
            raise RuntimeError(f"Tag not found: {tag}")

        repo_root = self._get_repo_root(source_dir)

        logger.info("Checking for changed files since %s", tag)
        cp = self._run(["git", "diff", "--name-only", f"{tag}..HEAD", "--", source_dir], capture_output=True, text=True)
        relative_files = [f for f in cp.stdout.splitlines() if f]
        absolute_files = [str((repo_root / f).resolve()) for f in relative_files]
        logger.info("Found %d changed file(s)", len(absolute_files))
        return absolute_files

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

    def _run(self, args, *, capture_output=False, text=None, allow_fail=False) -> subprocess.CompletedProcess:
        try:
            cp = subprocess.run(
                args,
                cwd=self.repo_path,
                capture_output=capture_output,
                text=(text if text is not None else capture_output),
                check=False,
            )
        except Exception as e:
            raise RuntimeError(f"Git exec failed: {' '.join(args)} ({e})") from e

        if cp.returncode != 0 and not allow_fail:
            raise RuntimeError(f"Git failed ({cp.returncode}): {' '.join(args)}")
        return cp
