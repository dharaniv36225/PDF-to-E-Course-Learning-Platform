"""FastAPI application entrypoint."""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.api.routes import api_router, health_router
from app.core.config import settings
from app.core.errors import register_exception_handlers
from app.core.logging import configure_logging, get_logger
from app.core.middleware import RateLimitMiddleware, RequestTimingMiddleware

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("Starting %s (%s)", settings.PROJECT_NAME, settings.ENVIRONMENT)
    yield
    logger.info("Shutting down %s", settings.PROJECT_NAME)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version="1.0.0",
        description=(
            "Convert PDFs into structured AI-powered learning courses with an "
            "RAG chatbot, quizzes and progress tracking."
        ),
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Process-Time"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(RequestTimingMiddleware)
    app.add_middleware(RateLimitMiddleware)

    register_exception_handlers(app)

    app.include_router(health_router)
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    return app


app = create_app()
