from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_api_key
from src.api.schemas.common import ApiResponse
from src.api.schemas.report import ReportRequest, ReportResponse
from src.core.database import get_db
from src.models.report import Report
from src.models.user import ApiKey

router = APIRouter()


@router.post("/report", response_model=ApiResponse)
async def submit_report(
    request: ReportRequest,
    api_key: ApiKey = Depends(get_api_key),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    """Submit feedback on a scan result."""
    report = Report(
        scan_id=request.scan_id,
        api_key_id=api_key.id,
        feedback_type=request.feedback_type,
        comment=request.comment,
        contact_email=request.contact_email,
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)

    return ApiResponse(
        ok=True,
        data=ReportResponse(
            report_id=report.id,
            scan_id=report.scan_id,
            feedback_type=report.feedback_type,
            status=report.status,
        ),
    )
