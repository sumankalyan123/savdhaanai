from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.middleware.error_handler import error_handler_middleware
from src.api.middleware.logging import LoggingMiddleware
from src.api.middleware.request_id import RequestIDMiddleware
from src.api.routes import card, health, report, scan
from src.core.config import settings
from src.core.database import engine


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    # Startup
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description="AI risk copilot — scam detection and beyond",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    lifespan=lifespan,
)

# Middleware (order matters — outermost first)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(LoggingMiddleware)
app.middleware("http")(error_handler_middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(health.router, prefix=settings.API_V1_PREFIX, tags=["health"])
app.include_router(scan.router, prefix=settings.API_V1_PREFIX, tags=["scan"])
app.include_router(card.router, prefix=settings.API_V1_PREFIX, tags=["card"])
app.include_router(report.router, prefix=settings.API_V1_PREFIX, tags=["report"])
