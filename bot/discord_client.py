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

    @client.event
    async def on_message(message: discord.Message) -> None:
        try:
            if message.author.bot:
                return
            if message.webhook_id is not None:
                return
            if message.channel.id != config.target_channel_id:
                return

            found = first_facebook_url(message.content)
            if not found:
                return

            cleaned = clean_facebook_url(found)
            title = fetch_title(cleaned, config.request_timeout, config.user_agent) or "Facebook Link"
            payload = format_clean_post(title, cleaned)

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
