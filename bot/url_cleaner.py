import re
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

# Matches http/https URLs, stopping at whitespace and common enclosing characters.
URL_PATTERN = re.compile(r"https?://[^\s<>()\[\]{}\"']+")

# All Facebook-owned domains we recognize as "Facebook URLs".
FACEBOOK_DOMAINS = {
    "facebook.com",
    "www.facebook.com",
    "m.facebook.com",
    "mbasic.facebook.com",
    "business.facebook.com",
    "fb.watch",
    "www.fb.watch",
}

# Query parameters that are pure tracking noise and carry no content value.
JUNK_QUERY_PARAMS = {
    "fbclid",        # Facebook click ID (added to every outbound link)
    "mibextid",      # Mobile app referral token
    "rdid",          # Redirect / referral ID
    "sfnsn",         # Surface/notification source
    "paipv",         # Internal A/B flag
    "__cft__",       # Content feed token
    "__tn__",        # Tracking node
    "ref",           # Generic referral source
    "refsrc",        # Referral source URL
    "referral_code",
    "referral_story_type",
    "tracking",
    "acontext",      # App context blob
    "notif_id",      # Notification identifier
    "notif_t",       # Notification type
    "locale",        # UI locale (not needed in a shared link)
}


def extract_urls(text: str) -> list[str]:
    """Return all http/https URLs found in text."""
    return URL_PATTERN.findall(text or "")


def is_facebook_url(url: str) -> bool:
    """Return True if the URL's host is a known Facebook domain."""
    try:
        parsed = urlparse(url)
    except ValueError:
        return False
    host = (parsed.netloc or "").lower()
    # Strip a leading www. that isn't in our domain set so subdomain checks
    # like business.facebook.com still match correctly.
    if host.startswith("www.") and host not in FACEBOOK_DOMAINS:
        host = host[4:]
    return host in FACEBOOK_DOMAINS


def _canonical_host(host: str) -> str:
    """Normalise a Facebook host to its preferred form.

    Collapses mobile subdomains to www.facebook.com and drops the redundant
    www. prefix on fb.watch short links.
    """
    host = host.lower()
    if host in {"m.facebook.com", "mbasic.facebook.com"}:
        return "www.facebook.com"
    if host == "www.fb.watch":
        return "fb.watch"
    return host


def clean_facebook_url(url: str) -> str:
    """Strip tracking parameters and normalise a Facebook URL.

    - Removes all known junk query params.
    - For marketplace item URLs, strips the entire query string because
      the item ID in the path is the only stable identifier.
    - Upgrades the scheme to https and drops URL fragments.
    """
    parsed = urlparse(url)
    host = _canonical_host(parsed.netloc)
    path = parsed.path or "/"

    # Marketplace item links are fully identified by item id in the path.
    # Query params on these are always referral/tracking noise.
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
        fragment="",  # fragments are never needed in shared links
        path=path,
    )
    return urlunparse(cleaned)


def first_facebook_url(text: str) -> str | None:
    """Return the first Facebook URL found in text, or None."""
    for url in extract_urls(text):
        if is_facebook_url(url):
            return url
    return None
