from __future__ import annotations

import uuid

from pydantic import BaseModel, Field

from src.core.constants import FeedbackType


class ReportRequest(BaseModel):
    scan_id: uuid.UUID
    feedback_type: FeedbackType
    comment: str | None = Field(default=None, max_length=2000)
    contact_email: str | None = Field(default=None, max_length=255)


class ReportResponse(BaseModel):
    report_id: uuid.UUID
    scan_id: uuid.UUID
    feedback_type: str
    status: str
    message: str = "Thank you for your feedback. It helps us improve."
