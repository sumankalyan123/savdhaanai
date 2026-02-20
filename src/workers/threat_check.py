from __future__ import annotations

from src.workers.celery_app import celery_app


@celery_app.task(name="cleanup_expired_content", bind=True, max_retries=3)
def cleanup_expired_content(self) -> dict:  # noqa: ARG001
    """Remove raw content from scans past their retention window."""
    # This runs as a periodic task
    # Implementation will use synchronous DB calls since Celery workers are sync
    return {"status": "ok", "message": "Cleanup task placeholder"}


@celery_app.task(name="generate_card_image", bind=True, max_retries=3)
def generate_card_image(self, card_id: str) -> dict:  # noqa: ARG001
    """Generate a shareable PNG image for a scam card."""
    # Placeholder — will use Pillow to render card image
    return {"status": "ok", "card_id": card_id, "message": "Card image generation placeholder"}
