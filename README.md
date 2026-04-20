# Discord Link Cleaner

Do you and your friends sit on Discord sharing links, only to look back a few days later and find a wall of unreadable URLs with zero context? This bot cleans them up automatically — stripping tracking garbage, resolving the page title, and reposting with the sender's name so your channel stays readable.

**Before:**
```
https://www.facebook.com/marketplace/item/123456789/?fbclid=IwAR0abc&mibextid=xyz
```

**After:**
```
**Vintage Bike for Sale**
https://www.facebook.com/marketplace/item/123456789/
Shared by @username
```

---

## Supported Sites

| Site | Tracking param stripping | Notes |
|---|---|---|
| Facebook (`facebook.com`, `m.facebook.com`, `fb.watch`, etc.) | Yes — `fbclid`, `mibextid`, `rdid`, and others | Mobile URLs normalized to `www.facebook.com` |
| Cars & Bids (`carsandbids.com`) | N/A | URL passed through as-is |

---

## Features

- Watches a single configured channel
- Detects links from supported sites and reposts with a human-readable title
- Resolves page title via OpenGraph metadata
- Optionally deletes the original message
- Ignores bots and webhooks
- Replies to `!version` (or `version`/`bot version`) in the target channel with the build version derived from the latest git commit date, overridable with the `BUILD_DATE` env var

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
    ports:
      - "8080:8080"
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
| `HEALTH_PORT` | No | `8080` | Port for the HTTP health check server |

---

## Health Check

The bot exposes an HTTP health endpoint on port 8080 (configurable via `HEALTH_PORT`) that reports the Discord connection state and channel accessibility.

**Endpoint:** `GET http://<host>:8080`

| HTTP Status | Body | Meaning |
|---|---|---|
| `200` | `{"status":"ok","discord":true,"channel":true}` | Fully healthy |
| `503` | `{"status":"degraded","discord":true,"channel":false}` | Connected to Discord but target channel is unreachable |
| `503` | `{"status":"down","discord":false,"channel":false}` | Not connected to Discord |

### Uptime Kuma

- **Monitor type:** HTTP(s) - Json Query
- **URL:** `http://<host>:8080`
- **Json Query:** `$.status`
- **Expected Value:** `ok`

## Dependency lockfile

Use `requirements.lock` for deterministic deployments and audits:

```bash
pip install -r requirements.lock
```

After bumping `requirements.txt`, update the lock manually (the repo relies on `requirements.lock` for Docker installs and audits) and rerun `./.venv/bin/pip-audit --requirement requirements.lock` locally before pushing.
