# Discord Facebook Link Cleaner Bot Plan

## Objective

Build a Discord bot that watches one dedicated channel for Facebook links and automatically turns messy pasted links into cleaner, more useful posts by:

- detecting Facebook URLs
- normalizing links copied from the browser address bar
- extracting the page or post title when possible
- reposting a compact, readable message
- optionally deleting the original message
- limiting all behavior to one configured channel

The result should be a cleaner Discord channel where Facebook links are easier to scan and take up less visual space.

---

## Success Criteria

A working bot should do all of the following:

1. Only operate in the configured Discord channel.
2. Detect Facebook links in new messages.
3. Clean obvious tracking or extra query parameters from pasted links.
4. Attempt to resolve a canonical URL.
5. Extract a usable title from the target page when available.
6. Post a compact replacement message such as:

```text
**{title}**
{clean_url}
```

7. Prevent the large ugly preview effect as much as possible.
8. Avoid looping on its own messages.
9. Log failures without crashing.
10. Be easy to run locally from VS Code and later host elsewhere if needed.

---

## Scope

### In Scope

- Discord bot using Python
- One dedicated channel for Facebook links
- Facebook URL cleanup
- Title extraction
- Message reposting
- Optional original message deletion
- Config via environment variables
- Logging and basic error handling
- Simple local execution from VS Code

### Out of Scope for v1

- Full dashboard or web UI
- Database
- Multi-server support beyond basic config
- Rich analytics
- Handling every possible social media platform
- Complex scraping for private Facebook content
- Slash commands beyond basic admin/testing helpers

---

## Key Product Decisions

### 1. Language and Stack

Use:

- Python 3.11+
- `discord.py`
- `httpx`
- `beautifulsoup4`
- `python-dotenv`

Reasoning:

- fast to build
- easy local debugging in VS Code
- strong Discord support
- simple dependency set

### 2. Bot Behavior Model

Recommended v1 behavior:

- user posts Facebook link
- bot detects it
- bot parses and cleans the URL
- bot attempts to fetch title metadata
- bot posts cleaned result
- bot optionally deletes the original message

This is better than replying inline if the goal is a tidy, link-only channel.

### 3. Title Source

Primary extraction order:

1. Open Graph title (`og:title`)
2. HTML `<title>`
3. fallback text like `Facebook Link`

### 4. URL Cleanup Strategy

The bot should remove common junk parameters when present, such as:

- `fbclid`
- `mibextid`
- `rdid`
- `sfnsn`
- `paipv`
- `__cft__`
- `__tn__`
- unrelated tracking query params

The bot should preserve parameters only when they appear necessary to identify the post.

### 5. Supported Facebook URL Types for v1

Target these first:

- `facebook.com/...`
- `www.facebook.com/...`
- `m.facebook.com/...`
- `fb.watch/...`

Optional if easy:

- `business.facebook.com/...`

### 6. Link Preview Reduction

Discord does not give full control over native embeds for ordinary user messages, so the bot strategy should be:

- repost a cleaned plain link with title
- keep formatting compact
- optionally delete the original
- optionally suppress embeds on the bot message if supported by the library path used

If embed suppression is unreliable, plain reposting still improves the channel a lot.

---

## Functional Requirements

## FR-1 Channel Restriction

The bot must only process messages in a configured channel ID.

**Acceptance test:**  
A Facebook link in any other channel is ignored.

## FR-2 Facebook Link Detection

The bot must detect one or more Facebook links in a message.

**Acceptance test:**  
A message with a Facebook URL is processed.  
A message with no Facebook URL is ignored.

## FR-3 Self-Protection

The bot must ignore:

- its own messages
- webhook messages if desired
- already processed content

**Acceptance test:**  
The bot never loops on its own repost.

## FR-4 URL Normalization

The bot must normalize Facebook links by:

- removing mobile subdomains where appropriate
- removing known junk query parameters
- preserving identifying path components
- resolving redirects when safe

**Acceptance test:**  
A messy copied URL becomes a smaller clean URL.

## FR-5 Metadata Retrieval

The bot must attempt to fetch title metadata from the cleaned URL.

**Acceptance test:**  
If the page is public and fetchable, the title is included.

## FR-6 Graceful Fallback

If title extraction fails, the bot must still repost a usable cleaned link.

**Acceptance test:**  
Network error or blocked page does not crash the bot.

## FR-7 Compact Repost Format

The bot must repost in a standard format.

Recommended format:

```text
**{title}**
{clean_url}
```

Optional alternative:

```text
{title} — {clean_url}
```

## FR-8 Optional Original Message Deletion

A config flag should control whether the original user message gets deleted after successful repost.

**Acceptance test:**  
When enabled, the original post disappears after bot repost.  
When disabled, both remain.

## FR-9 Logging

The bot must log:

- startup status
- guild connect status
- processed links
- cleanup changes
- metadata fetch failures
- delete failures
- unexpected exceptions

## FR-10 Configuration

The bot must read configuration from environment variables.

Required config:

- `DISCORD_TOKEN`
- `TARGET_CHANNEL_ID`

Optional config:

- `DELETE_ORIGINAL=true|false`
- `REQUEST_TIMEOUT=10`
- `USER_AGENT=...`
- `LOG_LEVEL=INFO`

---

## Non-Functional Requirements

## NFR-1 Reliability

The bot should keep running if one link fails.

## NFR-2 Simplicity

The project should be understandable in one VS Code workspace.

## NFR-3 Minimal Permissions

The bot should request only the permissions needed.

Recommended permissions:

- View Channel
- Send Messages
- Read Message History
- Manage Messages (only if deleting originals)
- Embed Links optional

## NFR-4 Maintainability

The codebase should be split into small modules, not one giant file.

## NFR-5 Security

The Discord token must never be hardcoded.

---

## Risks and Constraints

## Facebook Access Limitations

Facebook pages or posts may block scraping or require login. In those cases:

- title extraction may fail
- redirect resolution may be inconsistent
- some links may only produce a generic fallback title

This is expected and should be handled gracefully.

## Discord API Constraints

Deleting or replacing user messages requires the correct bot permissions.  
Some embed behavior is controlled by Discord and cannot be perfectly customized for all message types.

## Anti-Scraping Concerns

Do not hammer Facebook. Use:

- reasonable timeout
- one request per processed link
- simple headers
- no aggressive retry storm

---

## Repository Structure

Recommended project layout:

```text
discord-facebook-link-cleaner/
├─ .env.example
├─ .gitignore
├─ README.md
├─ requirements.txt
├─ main.py
├─ bot/
│  ├─ __init__.py
│  ├─ config.py
│  ├─ logger.py
│  ├─ url_cleaner.py
│  ├─ metadata.py
│  ├─ formatter.py
│  └─ discord_client.py
└─ tests/
   ├─ test_url_cleaner.py
   └─ test_formatter.py
```

---

## Module Responsibilities

## `main.py`

- entry point
- loads config
- starts bot
- top-level exception handling

## `bot/config.py`

- reads environment variables
- validates required values
- exposes typed config object

## `bot/logger.py`

- central logging setup

## `bot/url_cleaner.py`

- extracts URLs from message text
- identifies Facebook URLs
- normalizes domain/path/query
- strips junk parameters
- returns clean URL

## `bot/metadata.py`

- fetches page content with timeout
- parses Open Graph title or HTML title
- returns fallback when unavailable

## `bot/formatter.py`

- creates the final Discord message content
- centralizes output format

## `bot/discord_client.py`

- Discord event handlers
- channel filtering
- message processing orchestration
- repost/delete behavior

---

## Detailed Implementation Plan

## Phase 1 - Project Bootstrap

### Tasks

- create project folder
- create Python virtual environment
- install dependencies
- create starter file structure
- add `.env.example`
- add `.gitignore`
- create minimal `README.md`

### Deliverables

- project opens cleanly in VS Code
- bot starts without logic errors
- config loads successfully

---

## Phase 2 - Discord Bot Foundation

### Tasks

- create Discord application and bot user
- enable required message content intent
- invite bot to server with least privileges
- implement `on_ready`
- implement `on_message`
- confirm channel restriction works

### Deliverables

- bot connects successfully
- bot logs events
- bot sees messages in target channel only

### Acceptance Tests

- posting in target channel triggers log entry
- posting in another channel does nothing

---

## Phase 3 - URL Detection and Cleanup

### Tasks

- write URL extraction regex or parser
- filter to Facebook domains only
- normalize URL structure
- strip junk query parameters
- convert `m.facebook.com` to canonical domain if appropriate
- handle `fb.watch` carefully

### Deliverables

- standalone cleaner function with tests

### Acceptance Tests

Input:
```text
https://www.facebook.com/share/p/abc123/?mibextid=wwXIfr&fbclid=IwZXh0bgNhZW0CMTEAAR0...
```

Output should resemble:
```text
https://www.facebook.com/share/p/abc123/
```

---

## Phase 4 - Metadata Extraction

### Tasks

- fetch cleaned URL with `httpx`
- send browser-like user agent
- parse HTML with BeautifulSoup
- extract `og:title`
- fallback to `<title>`
- fallback to generic label

### Deliverables

- reusable metadata function
- timeout and exception handling

### Acceptance Tests

- public page returns readable title
- failed request returns fallback text without exception

---

## Phase 5 - Message Formatting and Posting

### Tasks

- define standard repost format
- post cleaned message to channel
- test formatting with title and without title
- decide whether to suppress embeds where possible

### Deliverables

- consistent compact reposts

### Acceptance Tests

Example output:
```text
**Parish Fish Fry Photos**
https://www.facebook.com/share/p/abc123/
```

---

## Phase 6 - Original Message Deletion

### Tasks

- add config toggle
- delete original only after successful repost
- handle permission errors cleanly

### Deliverables

- safe optional delete flow

### Acceptance Tests

- if repost succeeds and config enabled, original is deleted
- if delete fails, repost remains and error is logged

---

## Phase 7 - Hardening and Testing

### Tasks

- add unit tests for URL cleanup
- add tests for formatter
- test messages with:
  - one link
  - multiple links
  - text plus link
  - invalid Facebook link
  - mobile Facebook link
  - shortened link
- improve logs
- verify no loop behavior

### Deliverables

- stable v1 ready for daily use

---

## Recommended Environment Variables

Create `.env`:

```env
DISCORD_TOKEN=your_bot_token_here
TARGET_CHANNEL_ID=123456789012345678
DELETE_ORIGINAL=true
REQUEST_TIMEOUT=10
LOG_LEVEL=INFO
USER_AGENT=Mozilla/5.0 (compatible; DiscordLinkCleaner/1.0)
```

---

## VS Code Execution Workflow

## One-Time Setup

```bash
python -m venv .venv
```

### Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### macOS/Linux

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## Run the Bot

```bash
python main.py
```

## Debug in VS Code

Recommended steps:

- open the project folder
- select the `.venv` Python interpreter
- create a `.vscode/launch.json` for `main.py`
- run in debug mode and watch logs in terminal

---

## `requirements.txt` Draft

```text
discord.py>=2.5.0
httpx>=0.28.0
beautifulsoup4>=4.12.0
python-dotenv>=1.0.0
```

---

## Testing Checklist

## Basic Behavior

- [ ] Bot connects successfully
- [ ] Bot only reacts in target channel
- [ ] Bot ignores non-Facebook URLs
- [ ] Bot ignores its own messages

## Cleanup Behavior

- [ ] Removes `fbclid`
- [ ] Removes `mibextid`
- [ ] Keeps core identifying path
- [ ] Handles `m.facebook.com`
- [ ] Handles `fb.watch`

## Output Behavior

- [ ] Includes title when fetchable
- [ ] Falls back cleanly when not fetchable
- [ ] Reposts compact message
- [ ] Deletes original when enabled

## Failure Handling

- [ ] Network timeout does not crash bot
- [ ] Permission error does not crash bot
- [ ] Invalid URL does not crash bot

---

## Open Questions to Resolve Before Coding

These should be decided up front:

1. Should the bot delete the original message or leave it?
2. Should the bot process multiple Facebook links in one message or only the first?
3. Should the bot reply to the user or post a fresh replacement message?
4. Should generic fallback text say `Facebook Link`, `Facebook Post`, or something else?
5. Should the bot preserve any user-added text that came with the link?

Recommended defaults for v1:

- delete original: **yes**
- process multiple links: **first link only**
- repost style: **fresh replacement message**
- fallback label: **Facebook Link**
- preserve extra text: **no**, unless needed later

---

## Suggested v1 Build Order

Build in this order:

1. bot connects
2. bot filters to channel
3. bot detects Facebook link
4. bot cleans URL
5. bot reposts cleaned URL
6. bot fetches and adds title
7. bot deletes original
8. tests and polish

This avoids mixing scraping, Discord behavior, and cleanup logic all at once.

---

## Future Enhancements

Possible v2 additions:

- slash command to test a URL manually
- support Instagram or YouTube links
- preserve and repost user comment text above link
- cache processed URLs
- admin allowlist for who can trigger deletes
- richer normalization for more Facebook link formats
- Docker container deployment
- hosted deployment on a VPS or Railway/Render

---

## Definition of Done

The project is complete for v1 when:

- the bot runs locally from VS Code
- it only monitors the chosen channel
- it detects Facebook links
- it cleans obvious junk from copied URLs
- it reposts a compact title + link format
- it handles failures safely
- it optionally deletes the original message
- the repo contains a clear README and working `.env.example`

---

## Immediate Next Step

After approving this plan, the next execution task should be:

**Create the repository scaffold and write the first working version of the bot with channel filtering and Facebook URL cleanup only, before adding title extraction.**
