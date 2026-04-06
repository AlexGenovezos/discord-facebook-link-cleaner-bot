import sys
import types
import unittest
from unittest.mock import AsyncMock, MagicMock

if 'discord' not in sys.modules:
    fake_abc = types.ModuleType('discord.abc')
    fake_abc.Messageable = type('Messageable', (), {})
    fake_abc.User = type('User', (), {})
    fake_discord = types.ModuleType('discord')
    fake_discord.abc = fake_abc
    fake_discord.Forbidden = Exception
    fake_discord.HTTPException = Exception
    fake_discord.Intents = lambda: types.SimpleNamespace(message_content=False)
    fake_discord.Client = lambda *args, **kwargs: None
    sys.modules['discord'] = fake_discord
    sys.modules['discord.abc'] = fake_abc

from bot import discord_client


class DiscordClientTests(unittest.IsolatedAsyncioTestCase):
    async def test_notify_processing_failure_sends_channel_message(self) -> None:
        channel = AsyncMock()
        author = MagicMock()
        author.mention = "@alex"
        error = ValueError("boom boom")
        logger = MagicMock()

        await discord_client._notify_processing_failure(channel, author, error, logger)

        channel.send.assert_awaited_once()
        sent_text = channel.send.call_args.args[0]
        self.assertIn("⚠️", sent_text)
        self.assertIn("@alex", sent_text)
        logger.warning.assert_not_called()

    async def test_notify_processing_failure_logs_when_send_fails(self) -> None:
        channel = AsyncMock()
        channel.send.side_effect = RuntimeError("send down")
        author = MagicMock()
        author.mention = "@alex"
        error = RuntimeError("boom")
        logger = MagicMock()

        await discord_client._notify_processing_failure(channel, author, error, logger)

        channel.send.assert_awaited_once()
        logger.warning.assert_called_once()
