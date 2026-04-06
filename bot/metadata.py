from typing import Final

import httpx
from bs4 import BeautifulSoup

from .url_cleaner import is_facebook_url

MAX_HTML_RESPONSE_BYTES: Final[int] = 1_000_000


async def fetch_title(url: str, timeout: float, user_agent: str) -> str | None:
    """Fetch the human-readable title of a URL.

    Tries OpenGraph og:title first, falls back to the HTML <title> tag.
    Returns None if the request fails, times out, or the page isn't HTML.
    """
    headers = {"User-Agent": user_agent}
    body_chunks: bytearray | None = None
    try:
        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=timeout,
            headers=headers,
        ) as client:
            async with client.stream("GET", url) as response:
                response.raise_for_status()

                final_url = str(response.url)
                if not is_facebook_url(final_url):
                    return None

                content_type = response.headers.get("content-type", "").lower()
                if "text/html" not in content_type:
                    return None

                content_length = response.headers.get("content-length")
                if content_length:
                    try:
                        if int(content_length) > MAX_HTML_RESPONSE_BYTES:
                            return None
                    except ValueError:
                        pass

                body_chunks = bytearray()
                async for chunk in response.aiter_bytes():
                    if not chunk:
                        continue
                    if len(body_chunks) + len(chunk) > MAX_HTML_RESPONSE_BYTES:
                        return None
                    body_chunks.extend(chunk)
    except (httpx.HTTPError, httpx.InvalidURL):
        # Network errors, 4xx/5xx responses, and malformed URLs all return None
        # so the caller can fall back to a generic label.
        return None
    if not body_chunks:
        return None

    soup = BeautifulSoup(bytes(body_chunks), "html.parser")

    # Prefer OpenGraph title — it's usually the cleaned page title Facebook sets.
    og = soup.find("meta", property="og:title")
    if og and og.get("content"):
        return og.get("content").strip()

    # Fall back to the standard <title> element.
    if soup.title and soup.title.string:
        return soup.title.string.strip()

    return None
