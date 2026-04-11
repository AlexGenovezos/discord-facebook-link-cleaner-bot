import asyncio

from bot.config import load_config
from bot.discord_client import create_client
from bot.health import run_health_server
from bot.logger import setup_logging


async def _run() -> None:
    config = load_config()
    logger = setup_logging(config.log_level)
    client = create_client(config, logger)

    async with client:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(client.start(config.discord_token))
            tg.create_task(run_health_server(config.health_port, logger))


def main() -> None:
    asyncio.run(_run())


if __name__ == "__main__":
    main()
