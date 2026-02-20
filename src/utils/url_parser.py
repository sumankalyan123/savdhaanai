from __future__ import annotations

import re
from urllib.parse import urlparse

import tldextract


def extract_urls(text: str) -> list[str]:
    """Extract URLs from text content."""
    url_pattern = re.compile(
        r"https?://[^\s<>\"')\]]+|"
        r"(?:www\.)[^\s<>\"')\]]+|"
        r"(?:bit\.ly|t\.co|goo\.gl|tinyurl\.com|is\.gd)/[a-zA-Z0-9]+",
        re.IGNORECASE,
    )
    urls = url_pattern.findall(text)
    normalized = []
    for url in urls:
        if not url.startswith(("http://", "https://")):
            url = f"http://{url}"
        normalized.append(url.rstrip(".,;:!?)"))
    return list(dict.fromkeys(normalized))  # dedupe, preserve order


def get_domain(url: str) -> str:
    """Extract the registered domain from a URL."""
    extracted = tldextract.extract(url)
    if extracted.domain and extracted.suffix:
        return f"{extracted.domain}.{extracted.suffix}"
    return urlparse(url).hostname or ""


def is_shortened_url(url: str) -> bool:
    """Check if a URL is from a known URL shortener."""
    shorteners = {
        "bit.ly",
        "t.co",
        "goo.gl",
        "tinyurl.com",
        "is.gd",
        "ow.ly",
        "buff.ly",
        "tiny.cc",
        "rb.gy",
        "cutt.ly",
        "shorturl.at",
    }
    domain = get_domain(url)
    return domain in shorteners


def normalize_url(url: str) -> str:
    """Normalize a URL for consistent comparison."""
    url_lower = url.lower()
    if not url_lower.startswith(("http://", "https://")):
        url = f"http://{url}"
    parsed = urlparse(url)
    # Strip trailing slashes, normalize to lowercase host
    hostname = (parsed.hostname or "").lower()
    normalized = f"{parsed.scheme.lower()}://{hostname}"
    if parsed.port and parsed.port not in (80, 443):
        normalized += f":{parsed.port}"
    normalized += parsed.path.rstrip("/") or "/"
    if parsed.query:
        normalized += f"?{parsed.query}"
    return normalized
