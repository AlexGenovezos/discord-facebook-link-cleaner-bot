def format_clean_post(title: str, clean_url: str, author_mention: str | None = None) -> str:
    """Build the cleaned repost message that the bot sends to the channel.

    Format:
        **Page Title**
        https://example.com/...
        Shared by @username
    """
    attribution = f"\nShared by {author_mention}" if author_mention else ""
    if title and title.strip():
        return f"**{title.strip()}**\n{clean_url}{attribution}"
    return f"**Link**\n{clean_url}{attribution}"
