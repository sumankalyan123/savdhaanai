from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check() -> dict:
    return {
        "ok": True,
        "data": {"status": "healthy", "service": "savdhaan-ai", "version": "0.1.0"},
    }
