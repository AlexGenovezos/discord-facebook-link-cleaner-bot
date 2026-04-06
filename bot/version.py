"""Build version metadata for the Discord Facebook Link Cleaner bot."""

from __future__ import annotations

from datetime import date
import os
from typing import Final


BASE_VERSION: Final[str] = "0.1.0"
DATE_FORMAT: Final[str] = "%Y.%m.%d"


def _build_date() -> str:
    """Return the current build date string, preferring BUILD_DATE env."""
    if build_date_env := os.getenv("BUILD_DATE"):
        return build_date_env
    return date.today().strftime(DATE_FORMAT)


def _build_version() -> str:
    """Return BASE_VERSION plus the build date so every build reports its date."""
    return f"{BASE_VERSION}+{_build_date()}"


VERSION: Final[str] = _build_version()


def format_version_message() -> str:
    """Return a user-facing sentence describing the current build version."""
    return f"Discord Facebook Link Cleaner version {VERSION}"
