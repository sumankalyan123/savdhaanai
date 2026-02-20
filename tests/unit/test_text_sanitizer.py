from __future__ import annotations

from src.utils.text_sanitizer import hash_content, redact_pii, truncate_for_log


def test_hash_content_deterministic():
    assert hash_content("hello") == hash_content("hello")
    assert hash_content("hello") != hash_content("world")


def test_hash_content_is_sha256():
    h = hash_content("test")
    assert len(h) == 64  # SHA-256 hex digest length


def test_redact_pii_email():
    text = "Contact me at user@example.com"
    redacted = redact_pii(text)
    assert "user@example.com" not in redacted
    assert "[EMAIL_REDACTED]" in redacted


def test_redact_pii_phone():
    text = "Call me at +919876543210"
    redacted = redact_pii(text)
    assert "9876543210" not in redacted
    assert "[PHONE_REDACTED]" in redacted


def test_truncate_for_log():
    short = "Hello"
    assert truncate_for_log(short) == "Hello"

    long = "x" * 200
    truncated = truncate_for_log(long)
    assert len(truncated) == 103  # 100 + "..."
    assert truncated.endswith("...")
