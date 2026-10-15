"""FastAPI application entrypoint."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.api import api_router
from app.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import get_logger, setup_logging

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Lifespan event handler managing startup and shutdown routines."""
    settings = get_settings()
    setup_logging(log_level=settings.log_level)

    logger.info(
        "Starting %s v%s [env=%s, model=%s]",
        settings.app_name,
        settings.app_version,
        settings.app_env,
        settings.gemini_model,
    )
    yield

    logger.info("Shutting down %s...", settings.app_name)


def create_app() -> FastAPI:
    """Factory function to build and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Extract structured insurance claim fields from a claim narrative using Gemini.",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Return consistent errors for the two public routes.
    register_exception_handlers(app)
    app.include_router(api_router)

    return app


# Production ASGI instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    config = get_settings()
    uvicorn.run(
        "app.main:app",
        host=config.host,
        port=config.port,
        reload=(config.app_env.lower() == "development"),
        log_level=config.log_level.lower(),
    )
