"""Shared fixtures for the two-route API."""

import os
from unittest.mock import AsyncMock

import pytest
import httpx

os.environ["GEMINI_API_KEY"] = "test-gemini-key"

from app.config import get_settings
from app.main import app


@pytest.fixture(autouse=True)
def clear_settings_cache():
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
    app.dependency_overrides.clear()


@pytest.fixture
async def client():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client


@pytest.fixture
def mock_extraction_service():
    service = AsyncMock()
    service.model = "gemini-3.1-flash-lite"
    service.extract.return_value = {
        "Year Built": 1939,
        "Roof Damage (Yes/No)": "Yes",
        "Cause of Loss": "Hail",
    }
    return service
