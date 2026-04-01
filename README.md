# Discord Facebook Link Cleaner

A Discord bot that watches one channel and reposts Facebook links with tracking parameters stripped and the page title resolved.

**Before:** `https://www.facebook.com/marketplace/item/123456789/?fbclid=IwAR0abc&mibextid=xyz`
**After:** `**Vintage Bike for Sale**`
`https://www.facebook.com/marketplace/item/123456789/`
`Shared by @username`

## Features

- Watches a single configured channel
- Detects Facebook URLs (facebook.com, m.facebook.com, fb.watch, etc.)
- Strips tracking params: `fbclid`, `mibextid`, `rdid`, and others
- Normalizes mobile domains (`m.facebook.com` → `www.facebook.com`)
- Resolves the page title via OpenGraph metadata
- Optionally deletes the original message
- Ignores bots and webhooks

---

## Discord Bot Setup

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click **New Application**, give it a name, then go to the **Bot** tab
3. Click **Add Bot**, then **Reset Token** — copy the token (this is your `DISCORD_TOKEN`)
4. Under **Privileged Gateway Intents**, enable **Message Content Intent**
5. Go to **OAuth2 → URL Generator**:
   - Scopes: `bot`
   - Bot Permissions: `Send Messages`, `Read Message History`, `Manage Messages` (only if using `DELETE_ORIGINAL=true`)
6. Open the generated URL and invite the bot to your server
7. Right-click the target channel → **Copy Channel ID** (this is your `TARGET_CHANNEL_ID`)
   - If you don't see this option, enable Developer Mode under **User Settings → Advanced**

---

## Local Setup

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1
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

---

## Free Hosting (no credit card required)

### Option 1: Fly.io (recommended)

Fly.io's free allowance includes 3 shared VMs — enough to run this bot 24/7 without sleeping.

```bash
# Install the CLI
curl -L https://fly.io/install.sh | sh

# Sign up and log in
fly auth signup

# From the repo root:
fly launch          # Follow prompts: choose a name, region, skip DB, skip Redis
fly secrets set DISCORD_TOKEN=your_token_here
fly secrets set TARGET_CHANNEL_ID=123456789012345678
fly secrets set DELETE_ORIGINAL=true   # optional

fly deploy
fly logs            # tail live logs
```

Fly auto-detects the Dockerfile. The bot runs as a single-process app with no HTTP server needed — set the health check to `none` when prompted, or add this to your generated `fly.toml`:

```toml
[http_service]
  # Remove this entire section — the bot has no HTTP port
```

### Option 2: Oracle Cloud Free Tier (always free, most control)

Oracle gives you a free ARM VM (4 OCPUs, 24 GB RAM) that never expires.

1. Sign up at [cloud.oracle.com](https://cloud.oracle.com) (credit card required for identity, but you won't be charged)
2. Create a **Compute Instance** → select **Ampere A1** shape → choose **Always Free**
3. SSH in and install Docker:
   ```bash
   sudo dnf install -y docker
   sudo systemctl enable --now docker
   ```
4. Clone the repo, add a `.env` file, then:
   ```bash
   docker build -t discord-fb-bot .
   docker run -d --restart=always --env-file .env --name fb-bot discord-fb-bot
   ```

### Option 3: Railway

Railway has a free Hobby trial ($5 credit). After that it requires a paid plan, but setup is the simplest:

1. Push this repo to GitHub
2. Go to [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub repo**
3. Select your repo — Railway auto-detects the Dockerfile
4. Add environment variables under **Variables**

---

## Running with Docker (any host)

```bash
docker build -t discord-fb-bot .
docker run -d --restart=always \
  -e DISCORD_TOKEN=your_token \
  -e TARGET_CHANNEL_ID=123456789012345678 \
  -e DELETE_ORIGINAL=true \
  discord-fb-bot
```
