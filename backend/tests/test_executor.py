import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app

# All executor tests need both trainer-db and sandbox-db running.
# Use timeout=30 to give the 5-second DB timeout room to complete.

_TRANSPORT = ASGITransport(app=app)
_BASE = "http://test"
_TIMEOUT = 30.0


@pytest.mark.asyncio
async def test_valid_select_returns_columns_and_rows() -> None:
    async with AsyncClient(transport=_TRANSPORT, base_url=_BASE, timeout=_TIMEOUT) as client:
        response = await client.post(
            "/api/v1/execute", json={"query": "SELECT 1 AS num, 'hello' AS greeting"}
        )
    assert response.status_code == 200
    data = response.json()
    assert data["error"] is None
    assert data["columns"] == ["num", "greeting"]
    assert data["rows"] == [[1, "hello"]]


@pytest.mark.asyncio
async def test_insert_rejected_by_validator() -> None:
    async with AsyncClient(transport=_TRANSPORT, base_url=_BASE, timeout=_TIMEOUT) as client:
        response = await client.post(
            "/api/v1/execute", json={"query": "INSERT INTO t VALUES (1)"}
        )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["error"], str)
    assert data["columns"] == []
    assert data["rows"] == []


@pytest.mark.asyncio
async def test_drop_table_rejected_by_validator() -> None:
    async with AsyncClient(transport=_TRANSPORT, base_url=_BASE, timeout=_TIMEOUT) as client:
        response = await client.post(
            "/api/v1/execute", json={"query": "DROP TABLE employees"}
        )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["error"], str)
    assert "SELECT" in data["error"]


@pytest.mark.asyncio
async def test_timeout_returns_error() -> None:
    async with AsyncClient(transport=_TRANSPORT, base_url=_BASE, timeout=_TIMEOUT) as client:
        response = await client.post(
            "/api/v1/execute", json={"query": "SELECT pg_sleep(10)"}
        )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["error"], str)
    assert "5" in data["error"] or "время" in data["error"].lower()


@pytest.mark.asyncio
async def test_query_exceeding_max_length_returns_error() -> None:
    long_query = "a" * 2001
    async with AsyncClient(transport=_TRANSPORT, base_url=_BASE, timeout=_TIMEOUT) as client:
        response = await client.post("/api/v1/execute", json={"query": long_query})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["error"], str)
    assert data["columns"] == []
    assert data["rows"] == []


@pytest.mark.asyncio
async def test_error_is_null_on_success() -> None:
    async with AsyncClient(transport=_TRANSPORT, base_url=_BASE, timeout=_TIMEOUT) as client:
        response = await client.post(
            "/api/v1/execute", json={"query": "SELECT 42 AS answer"}
        )
    assert response.status_code == 200
    assert response.json()["error"] is None


@pytest.mark.asyncio
async def test_error_is_string_on_failure() -> None:
    async with AsyncClient(transport=_TRANSPORT, base_url=_BASE, timeout=_TIMEOUT) as client:
        response = await client.post(
            "/api/v1/execute", json={"query": "INSERT INTO t VALUES (1)"}
        )
    assert response.status_code == 200
    assert isinstance(response.json()["error"], str)
