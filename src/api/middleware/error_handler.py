from __future__ import annotations

import structlog
from fastapi import Request
from fastapi.responses import JSONResponse

from src.core.exceptions import (
    RateLimitExceededError,
    SavdhaanError,
)

logger = structlog.get_logger()

STATUS_MAP = {
    "INVALID_INPUT": 400,
    "UNAUTHORIZED": 401,
    "FORBIDDEN": 403,
    "NOT_FOUND": 404,
    "PAYLOAD_TOO_LARGE": 413,
    "UNSUPPORTED_MEDIA_TYPE": 415,
    "RATE_LIMIT_EXCEEDED": 429,
    "EXTERNAL_SERVICE_ERROR": 502,
    "INTERNAL_ERROR": 500,
}


async def error_handler_middleware(request: Request, call_next):  # noqa: ANN001
    try:
        return await call_next(request)
    except SavdhaanError as e:
        status_code = STATUS_MAP.get(e.code, 500)
        response_body = {
            "ok": False,
            "data": None,
            "error": {"code": e.code, "message": e.message},
            "meta": {"request_id": getattr(request.state, "request_id", None)},
        }

        if isinstance(e, RateLimitExceededError):
            return JSONResponse(
                status_code=status_code,
                content=response_body,
                headers={"Retry-After": str(e.retry_after)},
            )

        return JSONResponse(status_code=status_code, content=response_body)
    except Exception:
        await logger.aexception(
            "unhandled_exception",
            path=request.url.path,
            request_id=getattr(request.state, "request_id", None),
        )
        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "data": None,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                },
                "meta": {"request_id": getattr(request.state, "request_id", None)},
            },
        )
