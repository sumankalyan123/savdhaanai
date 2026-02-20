from __future__ import annotations

import uuid

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.report import Report

logger = structlog.get_logger()


async def get_report(db: AsyncSession, report_id: uuid.UUID) -> Report | None:
    """Get a report by ID."""
    result = await db.execute(select(Report).where(Report.id == report_id))
    return result.scalar_one_or_none()


async def get_reports_for_scan(db: AsyncSession, scan_id: uuid.UUID) -> list[Report]:
    """Get all reports for a scan."""
    result = await db.execute(select(Report).where(Report.scan_id == scan_id))
    return list(result.scalars().all())
