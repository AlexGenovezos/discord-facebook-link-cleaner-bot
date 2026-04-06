"""Build version metadata for the Discord Facebook Link Cleaner bot."""

from __future__ import annotations

from datetime import date, datetime
import os
from typing import Final


BASE_VERSION: Final[str] = ""
DATE_FORMAT: Final[str] = "%Y.%m.%d"
SEQUENCE_ENV_VARS: Final[tuple[str, ...]] = (
    "BUILD_SEQUENCE",
    "GITHUB_RUN_NUMBER",
    "GITHUB_RUN_ID",
    "CI_PIPELINE_ID",
    "CI_PIPELINE_NUMBER",
    "CI_JOB_NUMBER",
    "BUILD_NUMBER",
    "BITBUCKET_BUILD_NUMBER",
    "CIRCLE_BUILD_NUM",
    "DRONE_BUILD_NUMBER",
    "BUILDKITE_BUILD_NUMBER",
    "SEMAPHORE_BUILD_NUMBER",
)


def _build_date() -> str:
    """Return the current build date string, preferring BUILD_DATE env."""
    if build_date_env := os.getenv("BUILD_DATE"):
        return build_date_env
    return date.today().strftime(DATE_FORMAT)


def _sequence_from_env() -> str | None:
    """Return a numeric build sequence from common CI env vars, if set."""
    for env_name in SEQUENCE_ENV_VARS:
        if value := os.getenv(env_name):
            cleaned = "".join(ch for ch in value.strip() if ch.isdigit())
            if cleaned:
                return cleaned
    return None


def _timestamp_sequence() -> str:
    """Fallback sequence based on UTC time-of-day so each build is distinct."""
    return datetime.utcnow().strftime("%H%M%S")


def _build_version() -> str:
    """Return date plus optional build sequence suffix."""
    date_part = _build_date()
    sequence = _sequence_from_env() or _timestamp_sequence()
    base = f"{BASE_VERSION}+" if BASE_VERSION else ""
    return f"{base}{date_part}-{sequence}"


VERSION: Final[str] = _build_version()


def format_version_message() -> str:
    """Return a user-facing sentence describing the current build version."""
    return f"Discord Facebook Link Cleaner version {VERSION}"
