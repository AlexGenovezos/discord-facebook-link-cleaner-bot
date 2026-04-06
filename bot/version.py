"""Build version metadata for the Discord Facebook Link Cleaner bot."""

from __future__ import annotations

from pathlib import Path
import subprocess
from typing import Final


BASE_VERSION: Final[str] = "0.1.0"


def _git_commit_count() -> int | None:
    """Return the git commit count for the repository root or None on error."""
    try:
        repo_root = Path(__file__).resolve().parents[1]
        result = subprocess.run(
            ["git", "rev-list", "--count", "HEAD"],
            cwd=repo_root,
            capture_output=True,
            check=True,
            text=True,
        )
        return int(result.stdout.strip())
    except (subprocess.SubprocessError, ValueError):
        return None


def _build_version() -> str:
    """Return BASE_VERSION plus commit suffix when the repo is available."""
    commit_count = _git_commit_count()
    if commit_count is None:
        return BASE_VERSION
    return f"{BASE_VERSION}+{commit_count}"


VERSION: Final[str] = _build_version()


def format_version_message() -> str:
    """Return a user-facing sentence describing the current build version."""
    return f"Discord Facebook Link Cleaner version {VERSION}"
