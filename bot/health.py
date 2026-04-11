import asyncio
import json
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import discord

logger = logging.getLogger(__name__)


def _response(status: int, body: dict) -> bytes:
    payload = json.dumps(body).encode()
    reason = "OK" if status == 200 else "Service Unavailable"
    header = (
        f"HTTP/1.1 {status} {reason}\r\n"
        f"Content-Type: application/json\r\n"
        f"Content-Length: {len(payload)}\r\n"
        f"\r\n"
    ).encode()
    return header + payload


async def run_health_server(port: int, client: "discord.Client", channel_id: int) -> None:
    """HTTP health server for Uptime Kuma. Returns 200 when fully healthy, 503 otherwise."""

    async def handle(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        try:
            await reader.read(1024)

            discord_ok = client.is_ready()
            channel_ok = discord_ok and client.get_channel(channel_id) is not None

            if discord_ok and channel_ok:
                writer.write(_response(200, {"status": "ok", "discord": True, "channel": True}))
            elif discord_ok:
                writer.write(_response(503, {"status": "degraded", "discord": True, "channel": False}))
            else:
                writer.write(_response(503, {"status": "down", "discord": False, "channel": False}))

            await writer.drain()
        except (ConnectionResetError, asyncio.IncompleteReadError):
            pass
        finally:
            writer.close()
            await writer.wait_closed()

    server = await asyncio.start_server(handle, "0.0.0.0", port)
    logger.info("Health check server listening on port %s", port)
    async with server:
        await server.serve_forever()
