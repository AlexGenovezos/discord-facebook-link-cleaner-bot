import logging

import discord

from .config import Config
from .formatter import format_clean_post
from .metadata import fetch_title
from .url_cleaner import clean_facebook_url, first_facebook_url


def create_client(config: Config, logger: logging.Logger) -> discord.Client:
    intents = discord.Intents.default()
    intents.message_content = True

    client = discord.Client(intents=intents)

    @client.event
    async def on_ready() -> None:
        logger.info("Bot connected as %s (%s)", client.user, client.user.id if client.user else "unknown")
        logger.info(
            "Watching channel_id=%s | delete_original=%s",
            config.target_channel_id,
            config.delete_original,
        )

    @client.event
    async def on_message(message: discord.Message) -> None:
        try:
            if message.author.bot:
                logger.debug("Ignoring bot message id=%s", message.id)
                return
            if message.webhook_id is not None:
                logger.debug("Ignoring webhook message id=%s", message.id)
                return
            if message.channel.id != config.target_channel_id:
                logger.debug(
                    "Ignoring message id=%s in channel_id=%s (target=%s)",
                    message.id,
                    message.channel.id,
                    config.target_channel_id,
                )
                return

            logger.debug(
                "Received target-channel message id=%s author=%s content_len=%s",
                message.id,
                message.author.id,
                len(message.content or ""),
            )

            found = first_facebook_url(message.content)
            if not found:
                logger.debug("No Facebook URL found in message id=%s", message.id)
                return

            cleaned = clean_facebook_url(found)
            title = fetch_title(cleaned, config.request_timeout, config.user_agent) or "Facebook Link"
            payload = format_clean_post(title, cleaned, message.author.mention)

            try:
                await message.channel.send(payload, suppress_embeds=True)
            except TypeError:
                # Older discord.py paths may not support suppress_embeds.
                await message.channel.send(payload)

            logger.info("Processed Facebook link: %s -> %s", found, cleaned)

            if config.delete_original:
                try:
                    await message.delete()
                except discord.Forbidden:
                    logger.warning("Missing permission to delete original message %s", message.id)
                except discord.HTTPException as delete_error:
                    logger.warning("Failed to delete original message %s: %s", message.id, delete_error)
        except Exception as error:
            logger.exception("Unexpected failure while processing message %s: %s", message.id, error)

    return client
