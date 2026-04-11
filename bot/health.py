import asyncio
import logging


async def run_health_server(port: int, logger: logging.Logger) -> None:
    """Run a minimal HTTP server that returns 200 OK for Uptime Kuma health checks."""

    async def handle(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        try:
            await reader.read(1024)
            writer.write(
                b"HTTP/1.1 200 OK\r\n"
                b"Content-Type: text/plain\r\n"
                b"Content-Length: 2\r\n"
                b"\r\n"
                b"OK"
            )
            await writer.drain()
        finally:
            writer.close()

    server = await asyncio.start_server(handle, "0.0.0.0", port)
    logger.info("Health check server listening on port %s", port)
    async with server:
        await server.serve_forever()
