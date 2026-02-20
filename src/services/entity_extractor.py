from __future__ import annotations

import structlog
from anthropic import AsyncAnthropic

from src.api.schemas.scan import EntityData
from src.core.config import settings
from src.core.exceptions import LLMError
from src.utils.phone_parser import (
    extract_crypto_addresses,
    extract_emails,
    extract_phones,
    extract_upi_ids,
)
from src.utils.url_parser import extract_urls

logger = structlog.get_logger()

# LLM-based extraction is supplementary to regex — catches things like
# obfuscated URLs ("h t t p s : / / ...") or numbers written as words.
EXTRACTION_TOOL = {
    "name": "extract_entities",
    "description": "Extract suspicious entities from the message for threat analysis.",
    "input_schema": {
        "type": "object",
        "properties": {
            "urls": {
                "type": "array",
                "items": {"type": "string"},
                "description": (
                    "All URLs, links, and web addresses found"
                    " in the message (including obfuscated ones)."
                ),
            },
            "phones": {
                "type": "array",
                "items": {"type": "string"},
                "description": "All phone numbers found in the message.",
            },
            "emails": {
                "type": "array",
                "items": {"type": "string"},
                "description": "All email addresses found in the message.",
            },
            "crypto_addresses": {
                "type": "array",
                "items": {"type": "string"},
                "description": "All cryptocurrency wallet addresses found.",
            },
            "upi_ids": {
                "type": "array",
                "items": {"type": "string"},
                "description": "All UPI IDs found (format: name@bank).",
            },
        },
        "required": ["urls", "phones", "emails", "crypto_addresses", "upi_ids"],
    },
}


async def extract_entities(text: str) -> EntityData:
    """Extract entities using regex first, then LLM for anything missed."""
    # Phase 1: Regex extraction (fast, reliable)
    entities = EntityData(
        urls=extract_urls(text),
        phones=extract_phones(text),
        emails=extract_emails(text),
        crypto_addresses=extract_crypto_addresses(text),
        upi_ids=extract_upi_ids(text),
    )

    # Phase 2: LLM extraction for obfuscated entities (only if API key configured)
    if settings.ANTHROPIC_API_KEY:
        try:
            llm_entities = await _llm_extract(text)
            entities = _merge_entities(entities, llm_entities)
        except Exception:
            await logger.awarning("llm_entity_extraction_failed", exc_info=True)

    return entities


async def _llm_extract(text: str) -> EntityData:
    """Use Claude to extract entities that regex might miss."""
    client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    try:
        response = await client.messages.create(
            model=settings.CLAUDE_MODEL_FAST,
            max_tokens=1024,
            tools=[EXTRACTION_TOOL],
            tool_choice={"type": "tool", "name": "extract_entities"},
            messages=[
                {
                    "role": "user",
                    "content": f"Extract all entities from this message:\n\n{text}",
                }
            ],
        )

        for block in response.content:
            if block.type == "tool_use" and block.name == "extract_entities":
                return EntityData(**block.input)

    except Exception as e:
        raise LLMError(f"Entity extraction failed: {e}") from e

    return EntityData()


def _merge_entities(regex: EntityData, llm: EntityData) -> EntityData:
    """Merge regex and LLM results, deduplicating."""
    return EntityData(
        urls=list(dict.fromkeys(regex.urls + llm.urls)),
        phones=list(dict.fromkeys(regex.phones + llm.phones)),
        emails=list(dict.fromkeys(regex.emails + llm.emails)),
        crypto_addresses=list(dict.fromkeys(regex.crypto_addresses + llm.crypto_addresses)),
        upi_ids=list(dict.fromkeys(regex.upi_ids + llm.upi_ids)),
    )
