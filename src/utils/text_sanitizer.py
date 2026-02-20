from __future__ import annotations

import hashlib
import re


def hash_content(content: str) -> str:
    """Create a SHA-256 hash of the content for deduplication."""
    return hashlib.sha256(content.encode()).hexdigest()


def redact_pii(text: str) -> str:
    """Redact PII from text for logging purposes. Never log raw user content."""
    # Redact email addresses
    text = re.sub(
        r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "[EMAIL_REDACTED]",
        text,
    )
    # Redact phone numbers (Indian and international)
    text = re.sub(r"\+?\d{10,13}", "[PHONE_REDACTED]", text)
    # Redact UPI IDs
    return re.sub(r"[a-zA-Z0-9._-]+@[a-z]{2,}", "[UPI_REDACTED]", text)


def truncate_for_log(text: str, max_length: int = 100) -> str:
    """Truncate text for safe logging."""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."
