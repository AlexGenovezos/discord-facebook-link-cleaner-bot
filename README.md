# Discord Facebook Link Cleaner

Do you and your friends sit on Discord sharing Facebook Marketplace links, only to look back a few days later and find a wall of unreadable URLs with zero context? This bot cleans them up automatically — stripping tracking garbage, resolving the page title, and reposting with the sender's name so your channel stays readable.

**Before:**
```
https://www.facebook.com/marketplace/item/123456789/?fbclid=IwAR0abc&mibextid=xyz
```

**After:**
```
Vintage Bike for Sale
https://www.facebook.com/marketplace/item/123456789/
Shared by @username
```

---

## Features

- Watches a single configured channel
- Detects Facebook URLs (`facebook.com`, `m.facebook.com`, `fb.watch`, etc.)
- Strips tracking params: `fbclid`, `mibextid`, `rdid`, and others
- Normalizes mobile URLs (`m.facebook.com` → `www.facebook.com`)
- Resolves page title via OpenGraph metadata
- Optionally deletes the original message
- Ignores bots and webhooks
- Replies to `!version` (or `version`/`bot version`) in the target channel with the current build version so you always know what release you're running; the version uses `0.1.0` plus the build date (default `YYYY.MM.DD`, overridable with the `BUILD_DATE` env var) so every build reflects when it was created.

---

## Discord Bot Setup

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click **New Application**, give it a name, then go to the **Bot** tab
3. Click **Add Bot**, then **Reset Token** — copy the token (this is your `DISCORD_TOKEN`)
4. Under **Privileged Gateway Intents**, enable **Message Content Intent**
5. Go to **OAuth2 → URL Generator**:
   - Scopes: `bot`
   - Bot Permissions: `Send Messages`, `Read Message History`, `Manage Messages` (only needed if using `DELETE_ORIGINAL=true`)
6. Open the generated URL and invite the bot to your server
7. Right-click the target channel → **Copy Channel ID** (this is your `TARGET_CHANNEL_ID`)
   - If you don't see this option, enable Developer Mode under **User Settings → Advanced**

---

## Deployment

The recommended way to run this bot is via Docker using the pre-built image from GitHub Container Registry.

### Docker Compose (recommended)

Add to your `docker-compose.yml`:

```yaml
services:
  discord-bot:
    image: ghcr.io/alexgenovezos/discord-facebook-link-bot:latest
    env_file: .env
    restart: unless-stopped
```

Create a `.env` file alongside it:

```env
DISCORD_TOKEN=your_token_here
TARGET_CHANNEL_ID=123456789012345678
DELETE_ORIGINAL=true
```

Then run:

```bash
docker compose up -d discord-bot
```

To update to the latest image:

```bash
docker compose pull discord-bot && docker compose up -d discord-bot
```

### Local Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your values
python main.py
```

---

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `DISCORD_TOKEN` | Yes | — | Bot token from the Developer Portal |
| `TARGET_CHANNEL_ID` | Yes | — | Numeric ID of the channel to watch |
| `DELETE_ORIGINAL` | No | `false` | Delete the original message after reposting. Requires **Manage Messages** permission. |
| `REQUEST_TIMEOUT` | No | `10` | Seconds to wait when fetching a page title |
| `USER_AGENT` | No | `Mozilla/5.0 (compatible; DiscordLinkCleaner/1.0)` | HTTP User-Agent for title fetching |
| `LOG_LEVEL` | No | `INFO` | Log verbosity: `DEBUG`, `INFO`, `WARNING`, `ERROR` |

## Dependency lockfile

Use `requirements.lock` for deterministic deployments and audits:

```bash
pip install -r requirements.lock
```

After bumping `requirements.txt`, update the lock manually (the repo relies on `requirements.lock` for Docker installs and audits) and rerun `./.venv/bin/pip-audit --requirement requirements.lock` locally before pushing.
