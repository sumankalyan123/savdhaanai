"""Seed the scam_types reference table with the scam taxonomy."""
from __future__ import annotations

import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from src.core.config import settings

SCAM_TYPES = [
    {
        "code": "phishing",
        "label": "Phishing",
        "description": "Fake emails/websites impersonating trusted brands to steal credentials",
        "category": "credential_theft",
        "severity_default": "critical",
        "keywords": ["verify", "account", "suspended", "click here", "update"],
    },
    {
        "code": "smishing",
        "label": "SMS Phishing (Smishing)",
        "description": "Phishing via SMS — fake bank alerts, delivery notifications, etc.",
        "category": "credential_theft",
        "severity_default": "critical",
        "keywords": ["sms", "text", "kyc", "bank", "update"],
    },
    {
        "code": "vishing_reference",
        "label": "Voice Scam Reference",
        "description": "Message directing victim to call a scam phone number",
        "category": "social_engineering",
        "severity_default": "high",
        "keywords": ["call", "phone", "helpline", "customer care"],
    },
    {
        "code": "upi_fraud",
        "label": "UPI Fraud",
        "description": "Fake collect requests, QR code scams, or UPI PIN tricks",
        "category": "payment_fraud",
        "severity_default": "critical",
        "keywords": ["upi", "collect", "pin", "qr", "gpay", "phonepe", "paytm"],
    },
    {
        "code": "advance_fee",
        "label": "Advance Fee Scam",
        "description": "Requires upfront payment for a promised benefit that never arrives",
        "category": "financial_fraud",
        "severity_default": "high",
        "keywords": ["fee", "processing", "registration", "advance", "deposit"],
    },
    {
        "code": "lottery_prize",
        "label": "Lottery / Prize Scam",
        "description": "Fake lottery wins or prizes requiring fee payment to claim",
        "category": "financial_fraud",
        "severity_default": "critical",
        "keywords": ["won", "lottery", "prize", "claim", "congratulations", "lucky"],
    },
    {
        "code": "job_scam",
        "label": "Job Scam",
        "description": "Fake job offers requiring upfront payment or personal information",
        "category": "social_engineering",
        "severity_default": "high",
        "keywords": ["job", "offer", "hiring", "salary", "work from home", "registration fee"],
    },
    {
        "code": "investment_scam",
        "label": "Investment Scam",
        "description": "Fake investment opportunities promising unrealistic returns",
        "category": "financial_fraud",
        "severity_default": "critical",
        "keywords": ["invest", "returns", "guaranteed", "profit", "trading", "forex", "crypto"],
    },
    {
        "code": "tech_support",
        "label": "Tech Support Scam",
        "description": "Fake alerts claiming device is infected, requesting remote access or payment",
        "category": "social_engineering",
        "severity_default": "high",
        "keywords": ["virus", "infected", "microsoft", "apple", "support", "remote"],
    },
    {
        "code": "romance_scam",
        "label": "Romance Scam",
        "description": "Fake romantic interest building trust before requesting money",
        "category": "social_engineering",
        "severity_default": "high",
        "keywords": ["love", "relationship", "money", "help", "emergency", "stuck"],
    },
    {
        "code": "impersonation",
        "label": "Impersonation",
        "description": "Impersonating a known person, company, or government entity",
        "category": "social_engineering",
        "severity_default": "high",
        "keywords": ["government", "police", "tax", "irs", "income tax"],
    },
    {
        "code": "qr_code_scam",
        "label": "QR Code Scam",
        "description": "Malicious QR codes redirecting to phishing or payment fraud",
        "category": "payment_fraud",
        "severity_default": "high",
        "keywords": ["qr", "scan", "code", "pay"],
    },
    {
        "code": "otp_fraud",
        "label": "OTP Fraud",
        "description": "Tricking victims into sharing one-time passwords",
        "category": "credential_theft",
        "severity_default": "critical",
        "keywords": ["otp", "one time", "password", "verification code"],
    },
    {
        "code": "fake_app",
        "label": "Fake App",
        "description": "Directing victims to install malicious applications",
        "category": "malware",
        "severity_default": "critical",
        "keywords": ["download", "install", "app", "apk", "update"],
    },
    {
        "code": "crypto_scam",
        "label": "Cryptocurrency Scam",
        "description": "Fake crypto investments, giveaways, or wallet drainers",
        "category": "financial_fraud",
        "severity_default": "critical",
        "keywords": ["bitcoin", "crypto", "wallet", "airdrop", "token", "nft"],
    },
    {
        "code": "rental_scam",
        "label": "Rental Scam",
        "description": "Fake rental listings requiring deposits before viewing",
        "category": "financial_fraud",
        "severity_default": "high",
        "keywords": ["rent", "apartment", "deposit", "landlord", "lease"],
    },
    {
        "code": "delivery_scam",
        "label": "Delivery Scam",
        "description": "Fake delivery notifications with malicious links or fee requests",
        "category": "credential_theft",
        "severity_default": "high",
        "keywords": ["delivery", "package", "customs", "tracking", "courier"],
    },
    {
        "code": "charity_scam",
        "label": "Charity Scam",
        "description": "Fake charity appeals exploiting disasters or emotions",
        "category": "financial_fraud",
        "severity_default": "medium",
        "keywords": ["donate", "charity", "help", "disaster", "fund"],
    },
]


async def seed() -> None:
    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.begin() as conn:
        for st in SCAM_TYPES:
            await conn.execute(
                text("""
                    INSERT INTO scam_types (code, label, description, category, severity_default, keywords, is_active)
                    VALUES (:code, :label, :description, :category, :severity_default, :keywords, true)
                    ON CONFLICT (code) DO UPDATE SET
                        label = EXCLUDED.label,
                        description = EXCLUDED.description,
                        category = EXCLUDED.category,
                        severity_default = EXCLUDED.severity_default,
                        keywords = EXCLUDED.keywords
                """),
                {**st, "keywords": str(st["keywords"])},
            )
    await engine.dispose()
    print(f"Seeded {len(SCAM_TYPES)} scam types.")


if __name__ == "__main__":
    asyncio.run(seed())
