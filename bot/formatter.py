def format_clean_post(title: str, clean_url: str) -> str:
    if title and title.strip():
        return f"**{title.strip()}**\n{clean_url}"
    return f"**Facebook Link**\n{clean_url}"
