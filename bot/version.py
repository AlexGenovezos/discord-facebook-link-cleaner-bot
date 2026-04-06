"""Build version metadata for the Discord Facebook Link Cleaner bot."""

from typing import Final


VERSION: Final[str] = "0.1.0"


def format_version_message() -> str:
    """Return a user-facing sentence describing the current build version."""
    return f"Discord Facebook Link Cleaner version {VERSION}"
