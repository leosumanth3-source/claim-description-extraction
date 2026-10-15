"""Tests for the sole health endpoint."""


async def test_health(client):
    response = await client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "version" in response.json()


async def test_versioned_health_is_not_exposed(client):
    assert (await client.get("/api/v1/health")).status_code == 404
