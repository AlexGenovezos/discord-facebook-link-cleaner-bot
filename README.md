# Discord Facebook Link Cleaner

A Discord bot that watches one channel and reposts cleaned Facebook URLs in a compact format.

## Features (current)
- Restricts processing to one channel (`TARGET_CHANNEL_ID`)
- Detects Facebook links in messages
- Cleans common tracking parameters from Facebook URLs
- Reposts a compact message format
- Ignores bot and webhook messages

## Setup
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
cp .env.example .env
```

## Run
```bash
python main.py
```

## Environment
- `DISCORD_TOKEN` (required)
- `TARGET_CHANNEL_ID` (required)
- `DELETE_ORIGINAL` (optional, default `false`)
- `REQUEST_TIMEOUT` (optional, default `10`)
- `USER_AGENT` (optional)
- `LOG_LEVEL` (optional, default `INFO`)
