def format_clean_post(title: str, clean_url: str, author_mention: str | None = None) -> str:
    attribution = f"\nShared by {author_mention}" if author_mention else ""
    if title and title.strip():
        return f"**{title.strip()}**\n{clean_url}{attribution}"
    return f"**Facebook Link**\n{clean_url}{attribution}"
