import logging

import discord

from .config import Config
from .formatter import format_clean_post
from .metadata import fetch_title
from .url_cleaner import clean_facebook_url, first_facebook_url
from .version import VERSION, format_version_message


VERSION_COMMANDS = frozenset(
    {
        "!version",
        "bot version",
        "version",
    }
)



async def _notify_processing_failure(
    channel: discord.abc.Messageable,
    author: discord.abc.User,
    error: Exception,
    logger: logging.Logger,
) -> None:
    """Notify the channel that a Facebook link could not be cleaned."""

    mention = getattr(author, "mention", "the user")
    error_text = str(error) or error.__class__.__name__
    if len(error_text) > 160:
        error_text = f"{error_text[:157]}..."

    try:
        await channel.send(
            "⚠️ Unable to clean the Facebook link posted by "
            f"{mention}. The issue was logged ({error_text})."
        )
    except Exception as send_error:
        logger.warning(
            "Failed to notify channel after cleaning error (%s); original error=%s",
            send_error,
            error,
        )


def _is_version_request(content: str) -> bool:
    """Return True if the message explicitly asks for the bot version."""
    return content.strip().lower() in VERSION_COMMANDS


def create_client(config: Config, logger: logging.Logger) -> discord.Client:
    """Build and return a configured Discord client.

    The client listens for messages in the configured channel and reposts
    any Facebook links it finds in cleaned form.
    """
    intents = discord.Intents.default()
    intents.message_content = True  # Required to read message text

    client = discord.Client(intents=intents)

    @client.event
    async def on_ready() -> None:
        logger.info("Bot connected as %s (%s)", client.user, client.user.id if client.user else "unknown")
        logger.info("Build version %s", VERSION)
        logger.info(
            "Watching channel_id=%s | delete_original=%s",
            config.target_channel_id,
            config.delete_original,
        )

    @client.event
    async def on_message(message: discord.Message) -> None:
        try:
            # Ignore messages from bots and webhooks to avoid feedback loops.
            if message.author.bot:
                logger.debug("Ignoring bot message id=%s", message.id)
                return
            if message.webhook_id is not None:
                logger.debug("Ignoring webhook message id=%s", message.id)
                return

            # Only process messages in the configured target channel.
            if message.channel.id != config.target_channel_id:
                logger.debug(
                    "Ignoring message id=%s in channel_id=%s (target=%s)",
                    message.id,
                    message.channel.id,
                    config.target_channel_id,
                )
                return

            content = message.content or ""
            logger.debug(
                "Received target-channel message id=%s author=%s content_len=%s",
                message.id,
                message.author.id,
                len(content),
            )

            if _is_version_request(content):
                await message.channel.send(format_version_message())
                return

            # Look for the first Facebook URL in the message.
            found = first_facebook_url(content)
            if not found:
                logger.debug("No Facebook URL found in message id=%s", message.id)
                return

            # Clean the URL and resolve a human-readable title for it.
            cleaned = clean_facebook_url(found)
            title = await fetch_title(cleaned, config.request_timeout, config.user_agent) or "Facebook Link"
            payload = format_clean_post(title, cleaned, message.author.mention)

            # suppress_embeds prevents Discord from generating a link preview,
            # since our formatted message already contains the title.
            await message.channel.send(payload, suppress_embeds=True)

            logger.info("Processed Facebook link: %s -> %s", found, cleaned)

            # Optionally remove the original message so the channel only shows
            # the cleaned repost. Requires Manage Messages permission.
            if config.delete_original:
                try:
                    await message.delete()
                except discord.Forbidden:
                    logger.warning("Missing permission to delete original message %s", message.id)
                except discord.HTTPException as delete_error:
                    logger.warning("Failed to delete original message %s: %s", message.id, delete_error)
        except Exception as error:
            logger.exception("Unexpected failure while processing message %s: %s", message.id, error)
            await _notify_processing_failure(message.channel, message.author, error, logger)

    return client
