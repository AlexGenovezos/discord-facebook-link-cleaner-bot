from dataclasses import dataclass
import os

from dotenv import load_dotenv


@dataclass(frozen=True)
class Config:
    """Immutable runtime configuration loaded from environment variables."""

    discord_token: str
    target_channel_id: int
    delete_original: bool
    request_timeout: float
    user_agent: str
    log_level: str


def _positive_float(value: str | None, name: str) -> float:
    """Parse a string as a positive float, raising ValueError on bad input."""
    try:
        result = float(value or "")
    except ValueError:
        raise ValueError(f"{name} must be a positive number")
    if result <= 0:
        raise ValueError(f"{name} must be a positive number")
    return result


def _to_bool(value: str, default: bool = False) -> bool:
    """Parse common truthy strings ('true', '1', 'yes', 'on') to bool."""
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def load_config() -> Config:
    """Load and validate configuration from the environment (and .env file).

    Raises ValueError if any required variable is missing or invalid.
    """
    load_dotenv()

    token = os.getenv("DISCORD_TOKEN", "").strip()
    channel_id_raw = os.getenv("TARGET_CHANNEL_ID", "").strip()

    if not token:
        raise ValueError("DISCORD_TOKEN is required")
    if not channel_id_raw.isdigit():
        raise ValueError("TARGET_CHANNEL_ID must be a numeric Discord channel id")

    return Config(
        discord_token=token,
        target_channel_id=int(channel_id_raw),
        delete_original=_to_bool(os.getenv("DELETE_ORIGINAL"), default=False),
        request_timeout=_positive_float(os.getenv("REQUEST_TIMEOUT", "10"), "REQUEST_TIMEOUT"),
        user_agent=os.getenv(
            "USER_AGENT",
            "Mozilla/5.0 (compatible; DiscordLinkCleaner/1.0)",
        ),
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
    )
