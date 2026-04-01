from typing import Optional

import httpx
from bs4 import BeautifulSoup


def fetch_title(url: str, timeout: float, user_agent: str) -> Optional[str]:
    headers = {"User-Agent": user_agent}
    try:
        with httpx.Client(
            follow_redirects=True,
            timeout=timeout,
            headers=headers,
        ) as client:
            response = client.get(url)
            response.raise_for_status()
    except Exception:
        return None

    content_type = response.headers.get("content-type", "").lower()
    if "text/html" not in content_type:
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    og = soup.find("meta", property="og:title")
    if og and og.get("content"):
        return og.get("content").strip()

    if soup.title and soup.title.string:
        return soup.title.string.strip()

    return None
