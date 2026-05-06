import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_list_tasks_returns_200_and_non_empty() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/tasks")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


@pytest.mark.asyncio
async def test_list_tasks_no_solution_field() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/tasks")
    assert response.status_code == 200
    for item in response.json():
        assert "solution" not in item


@pytest.mark.asyncio
async def test_get_task_returns_correct_fields() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/tasks/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert "title" in data
    assert "description" in data
    assert "hints" in data
    assert "theory" in data
    assert "check_ordered" in data
    assert "check_columns_strict" in data


@pytest.mark.asyncio
async def test_get_task_no_solution_field() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/tasks/1")
    assert response.status_code == 200
    assert "solution" not in response.json()


@pytest.mark.asyncio
async def test_get_task_not_found() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/tasks/999")
    assert response.status_code == 404
