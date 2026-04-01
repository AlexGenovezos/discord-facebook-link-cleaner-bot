import httpx
from bs4 import BeautifulSoup


async def fetch_title(url: str, timeout: float, user_agent: str) -> str | None:
    """Fetch the human-readable title of a URL.

    Tries OpenGraph og:title first, falls back to the HTML <title> tag.
    Returns None if the request fails, times out, or the page isn't HTML.
    """
    headers = {"User-Agent": user_agent}
    try:
        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=timeout,
            headers=headers,
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
    except (httpx.HTTPError, httpx.InvalidURL):
        # Network errors, 4xx/5xx responses, and malformed URLs all return None
        # so the caller can fall back to a generic label.
        return None

    # Only parse HTML — skip PDFs, images, etc.
    content_type = response.headers.get("content-type", "").lower()
    if "text/html" not in content_type:
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    # Prefer OpenGraph title — it's usually the cleaned page title Facebook sets.
    og = soup.find("meta", property="og:title")
    if og and og.get("content"):
        return og.get("content").strip()

    # Fall back to the standard <title> element.
    if soup.title and soup.title.string:
        return soup.title.string.strip()

    return None
