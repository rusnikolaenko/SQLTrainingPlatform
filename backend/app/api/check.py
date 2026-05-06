from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import CheckResponse
from app.checker.checker import check
from app.db.models import Task
from app.db.session import get_db
from app.sandbox.validator import ValidationError, validate_query

router = APIRouter(prefix="/api/v1/tasks", tags=["checker"])


class CheckRequest(BaseModel):
    query: str


@router.post("/{task_id}/check", response_model=CheckResponse)
async def check_task(
    task_id: int,
    body: CheckRequest,
    db: AsyncSession = Depends(get_db),
) -> CheckResponse:
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if task is None:
        raise HTTPException(status_code=404, detail="Задание не найдено")

    try:
        validate_query(body.query)
    except ValidationError as exc:
        return CheckResponse(correct=False, message=exc.message, expected=[], got=[])

    verdict = await check(body.query, task)
    return CheckResponse(
        correct=verdict.correct,
        message=verdict.message,
        expected=verdict.expected,
        got=verdict.got,
    )
