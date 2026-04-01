from bot.config import load_config
from bot.discord_client import create_client
from bot.logger import setup_logging


def main() -> None:
    config = load_config()
    logger = setup_logging(config.log_level)
    client = create_client(config, logger)
    client.run(config.discord_token, log_handler=None)


if __name__ == "__main__":
    main()
