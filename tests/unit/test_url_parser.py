from __future__ import annotations

from src.utils.url_parser import extract_urls, get_domain, is_shortened_url, normalize_url


def test_extract_urls_basic():
    text = "Check this link: https://example.com/page and http://malicious.site/phish"
    urls = extract_urls(text)
    assert len(urls) == 2
    assert "https://example.com/page" in urls
    assert "http://malicious.site/phish" in urls


def test_extract_urls_shortened():
    text = "Visit bit.ly/abc123 for details"
    urls = extract_urls(text)
    assert len(urls) == 1
    assert "http://bit.ly/abc123" in urls


def test_extract_urls_no_urls():
    text = "This is a normal message with no links"
    urls = extract_urls(text)
    assert len(urls) == 0


def test_extract_urls_deduplicates():
    text = "Visit https://example.com twice: https://example.com"
    urls = extract_urls(text)
    assert len(urls) == 1


def test_get_domain():
    assert get_domain("https://www.example.com/path") == "example.com"
    assert get_domain("http://sub.domain.co.uk/page") == "domain.co.uk"


def test_is_shortened_url():
    assert is_shortened_url("https://bit.ly/abc123") is True
    assert is_shortened_url("https://t.co/xyz") is True
    assert is_shortened_url("https://example.com") is False


def test_normalize_url():
    assert normalize_url("HTTP://EXAMPLE.COM/") == "http://example.com/"
    assert normalize_url("https://example.com") == "https://example.com/"
    assert normalize_url("example.com/page") == "http://example.com/page"
