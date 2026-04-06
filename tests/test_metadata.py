import asyncio
from unittest.mock import patch

import httpx

from bot.metadata import MAX_HTML_RESPONSE_BYTES, fetch_title


class DummyResponse:
    def __init__(self, final_url: str, headers: dict[str, str], body: bytes) -> None:
        self.url = httpx.URL(final_url)
        self.headers = headers
        self._body = body

    async def aiter_bytes(self):
        if self._body:
            yield self._body

    def raise_for_status(self) -> None:
        return None


class FakeStreamContext:
    def __init__(self, response: DummyResponse) -> None:
        self._response = response

    async def __aenter__(self) -> DummyResponse:
        return self._response

    async def __aexit__(self, *_) -> bool:
        return False


def _run_fetch_with_response(response: DummyResponse) -> str | None:
    """Run fetch_title while forcing httpx.AsyncClient to return the provided response."""

    class FakeAsyncClient:
        def __init__(self, *_, **__):
            self._response = response

        async def __aenter__(self) -> "FakeAsyncClient":
            return self

        async def __aexit__(self, *_) -> bool:
            return False

        def stream(self, method: str, url: str) -> FakeStreamContext:
            return FakeStreamContext(self._response)

    async def _call() -> str | None:
        return await fetch_title("https://www.facebook.com/dialog/test", timeout=5, user_agent="pytest")

    with patch("bot.metadata.httpx.AsyncClient", FakeAsyncClient):
        return asyncio.run(_call())


def _make_response(
    final_url: str,
    headers: dict[str, str] | None = None,
    body: bytes = b"",
) -> DummyResponse:
    merged_headers = {
        "content-type": "text/html; charset=utf-8",
    }
    if headers:
        merged_headers.update(headers)
    return DummyResponse(final_url=final_url, headers=merged_headers, body=body)


def test_fetch_title_rejects_non_facebook_redirect() -> None:
    response = _make_response(
        final_url="https://example.com/page",
        body=b"<html><head><title>Safe</title></head><body></body></html>",
    )
    assert _run_fetch_with_response(response) is None


def test_fetch_title_respects_content_length_header() -> None:
    response = _make_response(
        final_url="https://www.facebook.com/page",
        headers={"content-length": str(MAX_HTML_RESPONSE_BYTES + 1)},
        body=b"<html><head><title>Safe</title></head><body></body></html>",
    )
    assert _run_fetch_with_response(response) is None


def test_fetch_title_respects_body_size_limit() -> None:
    response = _make_response(
        final_url="https://www.facebook.com/page",
        body=b"a" * (MAX_HTML_RESPONSE_BYTES + 1),
    )
    assert _run_fetch_with_response(response) is None


def test_fetch_title_prefer_og_title() -> None:
    body = b"""
        <html>
            <head>
                <meta property="og:title" content="OG Title">
                <title>Fallback Title</title>
            </head>
            <body></body>
        </html>
    """
    response = _make_response(final_url="https://www.facebook.com/page", body=body)
    assert _run_fetch_with_response(response) == "OG Title"
