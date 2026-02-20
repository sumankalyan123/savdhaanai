from __future__ import annotations

from src.core.constants import RiskLevel, ScamType

# Action templates per scam type
SCAM_ACTIONS: dict[str, list[str]] = {
    ScamType.PHISHING: [
        "Do NOT click any links in this message",
        "Do NOT enter any personal information",
        "Report the sender as spam/phishing",
        "If it claims to be from a known company, visit their official website directly "
        "(not through any link in this message)",
    ],
    ScamType.SMISHING: [
        "Do NOT click any links in this SMS",
        "Do NOT reply to this message",
        "Block the sender",
        "Report to your carrier by forwarding to 7726 (SPAM)",
    ],
    ScamType.UPI_FRAUD: [
        "Do NOT accept any collect request from unknown senders",
        "Remember: you do NOT need to enter your PIN to RECEIVE money",
        "Block this UPI ID in your payment app",
        "Report to your bank's fraud helpline",
    ],
    ScamType.ADVANCE_FEE: [
        "Do NOT send any money upfront",
        "Legitimate services do not require advance fees",
        "Do NOT share bank or UPI details",
        "Report this to cybercrime.gov.in or your local police",
    ],
    ScamType.LOTTERY_PRIZE: [
        "You cannot win a lottery you never entered",
        "Do NOT pay any 'processing fee' or 'tax'",
        "Do NOT share personal or banking details",
        "Block and report the sender",
    ],
    ScamType.JOB_SCAM: [
        "Legitimate employers NEVER ask for money to hire you",
        "Verify the company on their official website and LinkedIn",
        "Do NOT share Aadhaar, PAN, or banking details before verifying",
        "If the salary seems too good to be true, it probably is",
    ],
    ScamType.INVESTMENT_SCAM: [
        "No legitimate investment guarantees fixed high returns",
        "Check if the entity is registered with SEBI (India) or SEC (USA)",
        "Do NOT invest based on urgency or limited-time pressure",
        "Consult a registered financial advisor before investing",
    ],
    ScamType.TECH_SUPPORT: [
        "Legitimate companies do NOT cold-call about computer problems",
        "Do NOT give remote access to your computer",
        "Do NOT share passwords or OTPs",
        "Hang up and contact the company directly through their official number",
    ],
    ScamType.IMPERSONATION: [
        "Verify the sender's identity through a known, separate channel",
        "Do NOT act on urgent money requests without verifying",
        "Check the actual email address / phone number (not just the display name)",
        "Contact the person/organization directly using a number you already have",
    ],
    ScamType.OTP_FRAUD: [
        "NEVER share OTP with anyone — no bank or service will ask for it",
        "OTPs are for YOUR use only",
        "If someone asks for your OTP, it is a scam — no exceptions",
        "Report immediately to your bank",
    ],
    ScamType.CRYPTO_SCAM: [
        "No legitimate crypto investment guarantees returns",
        "Do NOT send cryptocurrency to unknown wallets",
        "Verify any platform on official crypto exchange listings",
        "Be extremely wary of 'celebrity endorsements' or 'exclusive groups'",
    ],
}

# Default actions per risk level
RISK_LEVEL_ACTIONS: dict[str, list[str]] = {
    RiskLevel.CRITICAL: [
        "We strongly recommend you do NOT engage with this message",
        "Block the sender immediately",
        "Report to relevant authorities",
    ],
    RiskLevel.HIGH: [
        "Exercise extreme caution",
        "Do NOT click links or share personal information",
        "Verify through official channels before taking any action",
    ],
    RiskLevel.MEDIUM: [
        "Proceed with caution",
        "Verify the sender and any claims independently",
        "Do NOT share personal or financial information without verification",
    ],
    RiskLevel.LOW: [
        "Stay alert — minor concerns noted",
        "If something feels off, trust your instincts and verify directly",
    ],
    RiskLevel.NONE: [
        "No scam indicators detected in our checks",
        "However, no automated system is perfect — if something feels wrong, verify directly",
    ],
}


def get_actions(scam_type: str, risk_level: str) -> list[str]:
    """Get recommended actions based on scam type and risk level."""
    actions = []

    # Add scam-type-specific actions
    if scam_type in SCAM_ACTIONS:
        actions.extend(SCAM_ACTIONS[scam_type])

    # Add risk-level actions
    if risk_level in RISK_LEVEL_ACTIONS:
        actions.extend(RISK_LEVEL_ACTIONS[risk_level])

    # Deduplicate while preserving order
    return list(dict.fromkeys(actions))
