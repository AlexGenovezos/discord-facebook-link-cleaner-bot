import re
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

URL_PATTERN = re.compile(r"https?://[^\s<>()\[\]{}\"']+")

FACEBOOK_DOMAINS = {
    "facebook.com",
    "www.facebook.com",
    "m.facebook.com",
    "mbasic.facebook.com",
    "business.facebook.com",
    "fb.watch",
    "www.fb.watch",
}

JUNK_QUERY_PARAMS = {
    "fbclid",
    "mibextid",
    "rdid",
    "sfnsn",
    "paipv",
    "__cft__",
    "__tn__",
    "ref",
    "refsrc",
    "referral_code",
    "referral_story_type",
    "tracking",
    "acontext",
    "notif_id",
    "notif_t",
    "locale",
}


def extract_urls(text: str) -> list[str]:
    return URL_PATTERN.findall(text or "")


def is_facebook_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
    except ValueError:
        return False
    host = (parsed.netloc or "").lower()
    if host.startswith("www.") and host not in FACEBOOK_DOMAINS:
        host = host[4:]
    return host in FACEBOOK_DOMAINS


def _canonical_host(host: str) -> str:
    host = host.lower()
    if host in {"m.facebook.com", "mbasic.facebook.com"}:
        return "www.facebook.com"
    if host == "www.fb.watch":
        return "fb.watch"
    return host


def clean_facebook_url(url: str) -> str:
    parsed = urlparse(url)
    host = _canonical_host(parsed.netloc)
    path = parsed.path or "/"

    # Marketplace item links are fully identified by item id in the path.
    # Query params are almost always referral/tracking noise.
    strip_all_query = path.startswith("/marketplace/item/")

    kept_params = []
    if not strip_all_query:
        for key, value in parse_qsl(parsed.query, keep_blank_values=True):
            if key.lower() in JUNK_QUERY_PARAMS:
                continue
            kept_params.append((key, value))

    query = urlencode(kept_params, doseq=True)

    cleaned = parsed._replace(
        scheme="https",
        netloc=host,
        query=query,
        fragment="",
        path=path,
    )
    return urlunparse(cleaned)


def first_facebook_url(text: str) -> str | None:
    for url in extract_urls(text):
        if is_facebook_url(url):
            return url
    return None
