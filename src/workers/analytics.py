from __future__ import annotations

from src.workers.celery_app import celery_app


@celery_app.task(name="aggregate_daily_stats", bind=True, max_retries=3)
def aggregate_daily_stats(self) -> dict:  # noqa: ARG001
    """Aggregate daily scan statistics."""
    return {"status": "ok", "message": "Daily stats aggregation placeholder"}


@celery_app.task(name="recalculate_abuse_scores", bind=True, max_retries=3)
def recalculate_abuse_scores(self) -> dict:  # noqa: ARG001
    """Recalculate abuse scores for all active API keys."""
    return {"status": "ok", "message": "Abuse score recalculation placeholder"}
