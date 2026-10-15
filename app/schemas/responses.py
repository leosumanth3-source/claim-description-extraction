"""Response models."""

from typing import Any

from pydantic import BaseModel


class Performance(BaseModel):
    """Execution details for a completed extraction request."""

    model: str
    latency_seconds: float
    populated_fields: int
    total_fields: int


class ClaimExtractionResponse(BaseModel):
    success: bool = True
    request_id: str
    data: dict[str, Any]
    performance: Performance


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail
