import pytest
from httpx import ASGITransport, AsyncClient

from app.checker.checker import COLUMNS_MESSAGE, ORDER_MESSAGE
from app.main import app

_TRANSPORT = ASGITransport(app=app)
_BASE = "http://test"
_TIMEOUT = 30.0


@pytest.mark.asyncio
async def test_correct_answer_returns_correct_true() -> None:
    async with AsyncClient(
        transport=_TRANSPORT, base_url=_BASE, timeout=_TIMEOUT
    ) as client:
        response = await client.post(
            "/api/v1/tasks/1/check",
            json={"query": "SELECT * FROM employees"},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["correct"] is True


@pytest.mark.asyncio
async def test_wrong_answer_returns_correct_false() -> None:
    async with AsyncClient(
        transport=_TRANSPORT, base_url=_BASE, timeout=_TIMEOUT
    ) as client:
        response = await client.post(
            "/api/v1/tasks/1/check",
            json={"query": "SELECT * FROM employees WHERE id = 1"},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["correct"] is False


@pytest.mark.asyncio
async def test_column_name_mismatch_returns_column_message() -> None:
    async with AsyncClient(
        transport=_TRANSPORT, base_url=_BASE, timeout=_TIMEOUT
    ) as client:
        response = await client.post(
            "/api/v1/tasks/1/check",
            json={
                "query": (
                    "SELECT id AS employee_id, name, department, salary FROM employees"
                )
            },
        )
    assert response.status_code == 200
    data = response.json()
    assert data["correct"] is False
    assert data["message"] == COLUMNS_MESSAGE


@pytest.mark.asyncio
async def test_ordered_task_wrong_order_returns_correct_false() -> None:
    async with AsyncClient(
        transport=_TRANSPORT, base_url=_BASE, timeout=_TIMEOUT
    ) as client:
        response = await client.post(
            "/api/v1/tasks/3/check",
            json={
                "query": (
                    "SELECT name, salary FROM employees ORDER BY salary ASC LIMIT 3"
                )
            },
        )
    assert response.status_code == 200
    data = response.json()
    assert data["correct"] is False
    assert data["message"] == ORDER_MESSAGE


@pytest.mark.asyncio
async def test_ordered_task_correct_order_returns_correct_true() -> None:
    async with AsyncClient(
        transport=_TRANSPORT, base_url=_BASE, timeout=_TIMEOUT
    ) as client:
        response = await client.post(
            "/api/v1/tasks/3/check",
            json={
                "query": (
                    "SELECT name, salary FROM employees ORDER BY salary DESC LIMIT 3"
                )
            },
        )
    assert response.status_code == 200
    data = response.json()
    assert data["correct"] is True
