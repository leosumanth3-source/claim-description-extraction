"""Tests for the sole extraction endpoint."""

from unittest.mock import AsyncMock
from uuid import UUID

from app.api.extract import get_extraction_service
from app.main import app


async def test_extract_claim(client, mock_extraction_service):
    async def override_service():
        return mock_extraction_service

    app.dependency_overrides[get_extraction_service] = override_service

    response = await client.post(
        "/api/v1/claims/extract",
        content="claim_description: A hailstorm damaged the roof.",
        headers={"content-type": "text/plain"},
    )

    assert response.status_code == 200
    result = response.json()
    assert result["success"] is True
    assert UUID(result["request_id"]).version == 4
    assert result["data"]["Roof Damage (Yes/No)"] == "Yes"
    assert result["performance"] == {
        "model": "gemini-3.1-flash-lite",
        "latency_seconds": result["performance"]["latency_seconds"],
        "populated_fields": 3,
        "total_fields": 3,
    }
    mock_extraction_service.extract.assert_awaited_once_with(
        "A hailstorm damaged the roof.", []
    )


async def test_extract_rejects_blank_claim(client):
    response = await client.post(
        "/api/v1/claims/extract",
        content="claim_description:   ",
        headers={"content-type": "text/plain"},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_CLAIM"


async def test_extract_accepts_one_custom_field(client, mock_extraction_service):
    async def override_service():
        return mock_extraction_service

    app.dependency_overrides[get_extraction_service] = override_service

    response = await client.post(
        "/api/v1/claims/extract",
        content=(
            "claim_description: A hailstorm damaged the roof.\n"
            "custom_field: Adjuster Name"
        ),
        headers={"content-type": "text/plain"},
    )

    assert response.status_code == 200
    mock_extraction_service.extract.assert_awaited_once_with(
        "A hailstorm damaged the roof.", ["Adjuster Name"]
    )


async def test_extract_returns_upstream_failure(client, mock_extraction_service):
    mock_extraction_service.extract = AsyncMock(side_effect=RuntimeError("Gemini unavailable"))

    async def override_service():
        return mock_extraction_service

    app.dependency_overrides[get_extraction_service] = override_service

    response = await client.post(
        "/api/v1/claims/extract",
        content="claim_description: A valid claim.",
        headers={"content-type": "text/plain"},
    )

    assert response.status_code == 502
    assert response.json()["error"]["code"] == "EXTRACTION_FAILED"
