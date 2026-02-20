from __future__ import annotations

import re

import phonenumbers


def extract_phones(text: str) -> list[str]:
    """Extract phone numbers from text, supporting Indian and international formats."""
    phones = []

    # Try phonenumbers library first (handles international formats)
    for match in phonenumbers.PhoneNumberMatcher(text, "IN"):
        formatted = phonenumbers.format_number(match.number, phonenumbers.PhoneNumberFormat.E164)
        phones.append(formatted)

    # Also try US region
    for match in phonenumbers.PhoneNumberMatcher(text, "US"):
        formatted = phonenumbers.format_number(match.number, phonenumbers.PhoneNumberFormat.E164)
        if formatted not in phones:
            phones.append(formatted)

    return phones


def extract_upi_ids(text: str) -> list[str]:
    """Extract UPI IDs from text (format: username@provider)."""
    upi_pattern = re.compile(
        r"[a-zA-Z0-9._-]+@(?:upi|ybl|okhdfcbank|oksbi|okicici|okaxis|paytm|apl|"
        r"ibl|axl|sbi|hdfcbank|icici|axisbank|kotak|indus|federal|idbi|rbl|"
        r"boi|pnb|cnrb|citi|sc|dbs|hsbc|jio|freecharge|gpay|phonepe|amazon)",
        re.IGNORECASE,
    )
    return list(dict.fromkeys(upi_pattern.findall(text)))


def extract_emails(text: str) -> list[str]:
    """Extract email addresses from text."""
    email_pattern = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", re.IGNORECASE)
    return list(dict.fromkeys(email_pattern.findall(text)))


def extract_crypto_addresses(text: str) -> list[str]:
    """Extract cryptocurrency wallet addresses from text."""
    patterns = [
        r"\b(1[a-km-zA-HJ-NP-Z1-9]{25,34})\b",  # Bitcoin
        r"\b(0x[a-fA-F0-9]{40})\b",  # Ethereum
        r"\b(T[a-zA-Z0-9]{33})\b",  # Tron
    ]
    addresses = []
    for pattern in patterns:
        addresses.extend(re.findall(pattern, text))
    return list(dict.fromkeys(addresses))
