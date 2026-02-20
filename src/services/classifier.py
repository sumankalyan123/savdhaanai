from __future__ import annotations

from dataclasses import dataclass, field

import structlog
from anthropic import AsyncAnthropic

from src.api.schemas.scan import EntityData, EvidenceItem
from src.core.config import settings
from src.core.constants import RiskLevel, ScamType

logger = structlog.get_logger()

CLASSIFICATION_TOOL = {
    "name": "classify_scam",
    "description": (
        "Classify the message and provide a risk assessment with evidence-grounded reasoning."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "risk_score": {
                "type": "integer",
                "minimum": 0,
                "maximum": 100,
                "description": "Risk score from 0 (no risk) to 100 (confirmed scam).",
            },
            "risk_level": {
                "type": "string",
                "enum": ["critical", "high", "medium", "low", "none"],
                "description": (
                    "Risk level based on score: critical (80-100),"
                    " high (60-79), medium (40-59),"
                    " low (20-39), none (0-19)."
                ),
            },
            "scam_type": {
                "type": "string",
                "enum": [t.value for t in ScamType],
                "description": "The most likely scam type. Use 'unknown' if uncertain.",
            },
            "explanation": {
                "type": "string",
                "description": (
                    "Clear, evidence-grounded explanation of why this is or"
                    " isn't a scam. Cite specific signals found in the message."
                    " Never use absolute language like 'safe' or"
                    " 'definitely a scam'."
                ),
            },
            "evidence_signals": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "signal": {"type": "string"},
                        "detail": {"type": "string"},
                    },
                    "required": ["signal", "detail"],
                },
                "description": (
                    "Specific signals that contributed to the classification."
                    " Each must cite something observable in the message"
                    " or threat intel."
                ),
            },
        },
        "required": ["risk_score", "risk_level", "scam_type", "explanation", "evidence_signals"],
    },
}


@dataclass
class ClassificationResult:
    risk_score: int = 0
    risk_level: str = RiskLevel.NONE
    scam_type: str = ScamType.UNKNOWN
    explanation: str = ""
    evidence: list[EvidenceItem] = field(default_factory=list)
    model_used: str = ""


SYSTEM_PROMPT = """\
You are Savdhaan AI's scam classification engine. Your job is to analyze \
messages and provide evidence-grounded risk assessments.

CRITICAL RULES:
1. NEVER use absolute language. Never say "safe", "definitely a scam", \
"guaranteed", or "100%".
2. ALWAYS ground your assessment in observable evidence from the message \
and threat intel.
3. If threat intel shows a URL is flagged, weight that heavily \
(increase score by 20-30).
4. If the domain is very new (< 7 days), weight that as suspicious \
(increase score by 10-20).
5. Consider these scam patterns: urgency, threats, too-good-to-be-true \
offers, requests for personal info, suspicious links, impersonation of \
known brands, unusual payment methods.
6. For low-risk messages, explicitly state "no automated system is \
perfect" in your explanation.
7. Be specific about what you found and what you couldn't check.

SCORE GUIDE:
- 80-100 (critical): Multiple strong scam indicators. Flagged URLs, \
brand impersonation + malicious link, known scam template.
- 60-79 (high): Several warning signs. New domains, urgency + money \
request, suspicious patterns.
- 40-59 (medium): Some suspicious elements but mixed signals. Could be \
aggressive marketing or a scam.
- 20-39 (low): Minor concerns but likely legitimate. Unusual tone or \
minor red flags.
- 0-19 (none): No scam indicators detected. Normal communication."""


async def classify_content(
    text: str,
    entities: EntityData,
    threat_evidence: list[EvidenceItem],
) -> ClassificationResult:
    """Classify content using Claude with structured tool_use output."""
    if not settings.ANTHROPIC_API_KEY:
        return _fallback_classification(text, threat_evidence)

    client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    # Build context for the LLM
    threat_context = ""
    if threat_evidence:
        threat_lines = []
        for e in threat_evidence:
            status = "FLAGGED" if e.is_threat else "clean"
            threat_lines.append(f"  - [{status}] {e.source}: {e.detail}")
        threat_context = "\n\nThreat intelligence results:\n" + "\n".join(threat_lines)

    entity_context = ""
    all_entities = (
        entities.urls
        + entities.phones
        + entities.emails
        + entities.upi_ids
        + entities.crypto_addresses
    )
    if all_entities:
        entity_context = f"\n\nExtracted entities: {', '.join(all_entities[:20])}"

    user_message = (
        f"Analyze this message for scam risk:\n\n---\n{text}\n---{entity_context}{threat_context}"
    )

    try:
        # Use fast model first
        model = settings.CLAUDE_MODEL_FAST
        response = await client.messages.create(
            model=model,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=[CLASSIFICATION_TOOL],
            tool_choice={"type": "tool", "name": "classify_scam"},
            messages=[{"role": "user", "content": user_message}],
        )

        for block in response.content:
            if block.type == "tool_use" and block.name == "classify_scam":
                data = block.input
                evidence = [
                    EvidenceItem(source="pattern_analysis", detail=s["detail"], is_threat=True)
                    for s in data.get("evidence_signals", [])
                ]
                # Merge threat intel evidence
                evidence = threat_evidence + evidence

                return ClassificationResult(
                    risk_score=data["risk_score"],
                    risk_level=data["risk_level"],
                    scam_type=data["scam_type"],
                    explanation=data["explanation"],
                    evidence=evidence,
                    model_used=model,
                )

    except Exception as e:
        await logger.awarning("classification_failed", error=str(e))
        return _fallback_classification(text, threat_evidence)

    return _fallback_classification(text, threat_evidence)


def _fallback_classification(
    _text: str, threat_evidence: list[EvidenceItem]
) -> ClassificationResult:
    """Fallback when LLM is unavailable — use threat intel signals only."""
    threat_count = sum(1 for e in threat_evidence if e.is_threat)

    if threat_count >= 2:
        score = 75
        level = RiskLevel.HIGH
    elif threat_count == 1:
        score = 55
        level = RiskLevel.MEDIUM
    else:
        score = 10
        level = RiskLevel.NONE

    return ClassificationResult(
        risk_score=score,
        risk_level=level,
        scam_type=ScamType.UNKNOWN,
        explanation=(
            "Analysis based on threat intelligence signals only (LLM unavailable). "
            f"Found {threat_count} threat indicator(s). "
            "No automated system is perfect — verify through official channels if unsure."
        ),
        evidence=threat_evidence,
        model_used="fallback",
    )
