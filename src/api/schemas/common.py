from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class ApiResponse(BaseModel):
    ok: bool
    data: Any | None = None
    error: ApiError | None = None
    meta: dict[str, Any] | None = None


class ApiError(BaseModel):
    code: str
    message: str
    details: dict[str, Any] | None = None
