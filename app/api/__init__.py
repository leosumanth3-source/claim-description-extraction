"""The application's two HTTP route groups."""

from fastapi import APIRouter

from app.api.extract import router as extraction_router
from app.api.health import router as health_router
from app.config import get_settings

_settings = get_settings()

# Health is kept at the root for deployment probes.
api_router = APIRouter()
api_router.include_router(health_router)

# The single business endpoint is versioned.
_v1 = APIRouter(prefix=_settings.api_prefix)
_v1.include_router(extraction_router)
api_router.include_router(_v1)
