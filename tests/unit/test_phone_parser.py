from __future__ import annotations

from src.utils.phone_parser import extract_crypto_addresses, extract_emails, extract_upi_ids


def test_extract_emails():
    text = "Contact us at support@example.com or admin@test.org"
    emails = extract_emails(text)
    assert len(emails) == 2
    assert "support@example.com" in emails
    assert "admin@test.org" in emails


def test_extract_emails_none():
    text = "No email here"
    assert extract_emails(text) == []


def test_extract_upi_ids():
    text = "Pay to merchant@upi or user@paytm for the order"
    upis = extract_upi_ids(text)
    assert len(upis) == 2
    assert "merchant@upi" in upis
    assert "user@paytm" in upis


def test_extract_upi_ids_none():
    text = "No UPI ID in this message"
    assert extract_upi_ids(text) == []


def test_extract_crypto_addresses():
    text = "Send to 0x742d35Cc6634C0532925a3b844Bc9e7595f2bD38"
    addresses = extract_crypto_addresses(text)
    assert len(addresses) == 1
    assert "0x742d35Cc6634C0532925a3b844Bc9e7595f2bD38" in addresses
