import logging


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Configure the root logger and return the bot's named logger.

    All output goes to stdout so it's captured by Docker / systemd / Fly.io
    log collectors without any extra configuration.
    """
    logging.basicConfig(
        level=getattr(logging, level, logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    return logging.getLogger("discord_facebook_link_cleaner")
