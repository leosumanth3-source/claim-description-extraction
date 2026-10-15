"""GET /health"""

from fastapi import APIRouter

from app.config import get_settings
from app.schemas import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse, summary="Health Check")
async def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        version=settings.app_version,
    )
