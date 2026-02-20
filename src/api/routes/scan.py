from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_api_key
from src.api.middleware.rate_limiter import check_rate_limit
from src.api.schemas.common import ApiResponse
from src.api.schemas.scan import ScanRequest
from src.core.constants import (
    MAX_IMAGE_SIZE_MB,
    SUPPORTED_IMAGE_TYPES,
    Channel,
    ScanCategory,
)
from src.core.database import get_db
from src.core.exceptions import NotFoundError, PayloadTooLargeError, UnsupportedMediaTypeError
from src.models.user import ApiKey
from src.services.scan_service import ScanService

router = APIRouter()


@router.post("/scan", response_model=ApiResponse)
async def create_scan(
    request: ScanRequest,
    api_key: ApiKey = Depends(get_api_key),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    """Scan text content for scam indicators."""
    await check_rate_limit(str(api_key.id), api_key.plan)

    service = ScanService(db)
    result = await service.scan_text(
        content=request.content,
        content_type=request.content_type,
        channel=request.channel,
        category=request.category,
        locale=request.locale,
        api_key=api_key,
    )
    return ApiResponse(ok=True, data=result)


@router.post("/scan/image", response_model=ApiResponse)
async def create_image_scan(
    file: UploadFile = File(...),
    channel: Channel | None = Form(default=None),
    category: ScanCategory = Form(default=ScanCategory.SCAM_CHECK),
    locale: str = Form(default="en"),
    api_key: ApiKey = Depends(get_api_key),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    """Scan an image for scam indicators (OCR + analysis)."""
    await check_rate_limit(str(api_key.id), api_key.plan)

    if file.content_type not in SUPPORTED_IMAGE_TYPES:
        raise UnsupportedMediaTypeError(
            f"Unsupported image type: {file.content_type}. "
            f"Supported: {', '.join(SUPPORTED_IMAGE_TYPES)}"
        )

    contents = await file.read()
    if len(contents) > MAX_IMAGE_SIZE_MB * 1024 * 1024:
        raise PayloadTooLargeError(f"Image exceeds {MAX_IMAGE_SIZE_MB}MB limit")

    service = ScanService(db)
    result = await service.scan_image(
        image_data=contents,
        content_type=file.content_type or "image/jpeg",
        channel=channel,
        category=category,
        locale=locale,
        api_key=api_key,
    )
    return ApiResponse(ok=True, data=result)


@router.get("/scan/{scan_id}", response_model=ApiResponse)
async def get_scan(
    scan_id: uuid.UUID,
    api_key: ApiKey = Depends(get_api_key),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    """Retrieve a previous scan result."""
    service = ScanService(db)
    result = await service.get_scan(scan_id=scan_id, api_key_id=api_key.id)
    if result is None:
        raise NotFoundError("Scan", str(scan_id))
    return ApiResponse(ok=True, data=result)
