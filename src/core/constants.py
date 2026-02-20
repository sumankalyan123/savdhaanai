from __future__ import annotations

from enum import StrEnum


class RiskLevel(StrEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"
    INSUFFICIENT = "insufficient"


class ScamType(StrEnum):
    PHISHING = "phishing"
    SMISHING = "smishing"
    VISHING_REFERENCE = "vishing_reference"
    UPI_FRAUD = "upi_fraud"
    ADVANCE_FEE = "advance_fee"
    LOTTERY_PRIZE = "lottery_prize"
    JOB_SCAM = "job_scam"
    INVESTMENT_SCAM = "investment_scam"
    TECH_SUPPORT = "tech_support"
    ROMANCE_SCAM = "romance_scam"
    IMPERSONATION = "impersonation"
    QR_CODE_SCAM = "qr_code_scam"
    OTP_FRAUD = "otp_fraud"
    FAKE_APP = "fake_app"
    CRYPTO_SCAM = "crypto_scam"
    RENTAL_SCAM = "rental_scam"
    DELIVERY_SCAM = "delivery_scam"
    CHARITY_SCAM = "charity_scam"
    UNKNOWN = "unknown"


class ContentType(StrEnum):
    TEXT = "text"
    IMAGE = "image"


class Channel(StrEnum):
    SMS = "sms"
    WHATSAPP = "whatsapp"
    EMAIL = "email"
    SOCIAL_DM = "social_dm"
    WEBSITE = "website"
    OTHER = "other"


class ScanCategory(StrEnum):
    SCAM_CHECK = "scam_check"
    JOB_OFFER = "job_offer"
    RENTAL_LEASE = "rental_lease"
    INVESTMENT = "investment"
    CONTRACT = "contract"
    AUTO = "auto"


class FeedbackType(StrEnum):
    CONFIRMED_SCAM = "confirmed_scam"
    FALSE_POSITIVE = "false_positive"
    FALSE_NEGATIVE = "false_negative"
    HELPFUL = "helpful"
    NOT_HELPFUL = "not_helpful"


class ReportStatus(StrEnum):
    PENDING = "pending"
    REVIEWED = "reviewed"
    ACTIONED = "actioned"


class ResponseLevel(StrEnum):
    FULL = "full"
    REDUCED = "reduced"
    MINIMAL = "minimal"
    THROTTLED = "throttled"


class AbuseEventType(StrEnum):
    HIGH_FREQUENCY = "high_frequency"
    ITERATIVE_TESTING = "iterative_testing"
    HIGH_FLAG_RATE = "high_flag_rate"
    ENTITY_REUSE = "entity_reuse"
    BURST_PATTERN = "burst_pattern"
    RAPID_ACCOUNT = "rapid_account"


class ThreatSource(StrEnum):
    GOOGLE_SAFE_BROWSING = "google_safe_browsing"
    PHISHTANK = "phishtank"
    URLHAUS = "urlhaus"
    SPAMHAUS = "spamhaus"
    WHOIS = "whois"


# Risk score ranges
RISK_THRESHOLDS = {
    RiskLevel.CRITICAL: (80, 100),
    RiskLevel.HIGH: (60, 79),
    RiskLevel.MEDIUM: (40, 59),
    RiskLevel.LOW: (20, 39),
    RiskLevel.NONE: (0, 19),
}

# API key prefix
API_KEY_PREFIX = "svd_"
API_KEY_LENGTH = 32

# Processing limits
MAX_TEXT_LENGTH = 10_000
MAX_IMAGE_SIZE_MB = 10
SUPPORTED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}

# Threat intel timeouts (seconds)
THREAT_INTEL_TIMEOUT = 5.0
THREAT_INTEL_PER_SOURCE_TIMEOUT = 3.0
