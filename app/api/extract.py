"""The single claim-extraction endpoint."""

import time
from uuid import uuid4

from fastapi import APIRouter, Body, Depends

from app.config import get_settings
from app.core.exceptions import ExtractionError, InvalidClaimError
from app.core.logging import get_logger
from app.schemas import ClaimExtractionRequest, ClaimExtractionResponse, Performance
from app.services.extraction import ExtractionService

logger = get_logger(__name__)

router = APIRouter(prefix="/claims", tags=["Extraction"])


async def get_extraction_service() -> ExtractionService:
    """Create the extraction service for a request."""
    return ExtractionService(get_settings())


def _count_populated(data: dict) -> int:
    return sum(
        1 for v in data.values()
        if v is not None and v != [] and v != ""
    )


@router.post(
    "/extract",
    response_model=ClaimExtractionResponse,
    summary="Extract Claim Fields",
    description=(
        "Accepts plain text in the format `claim_description: ...` followed by an "
        "optional `custom_field: ...`, then returns the standard claim fields."
    ),
)
async def extract_claim(
    body: str = Body(
        ...,
        media_type="text/plain",
        max_length=100_000,
        openapi_examples={
            "plain_text_template": {
                "summary": "Claim extraction template",
                "value": "claim_description: \ncustom_field: ",
            }
        },
    ),
    service: ExtractionService = Depends(get_extraction_service),
) -> ClaimExtractionResponse:
    try:
        request = ClaimExtractionRequest.from_plain_text(body)
    except ValueError as exc:
        raise InvalidClaimError(str(exc)) from exc

    custom_fields = [request.custom_field] if request.custom_field else []

    logger.info(
        "Extraction request — desc_len=%d custom_field=%s",
        len(request.claim_description),
        bool(custom_fields),
    )

    start = time.perf_counter()

    try:
        data = await service.extract(request.claim_description, custom_fields)
    except ValueError as exc:
        raise InvalidClaimError(str(exc)) from exc
    except Exception as exc:
        logger.error("Extraction failed: %s", exc, exc_info=True)
        raise ExtractionError(str(exc)) from exc

    latency = round(time.perf_counter() - start, 3)
    logger.info("Extraction done in %.3fs", latency)

    return ClaimExtractionResponse(
        success=True,
        request_id=str(uuid4()),
        data=data,
        performance=Performance(
            model=service.model,
            latency_seconds=latency,
            populated_fields=_count_populated(data),
            total_fields=len(data),
        ),
    )
