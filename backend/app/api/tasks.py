from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import TaskDetail, TaskListItem
from app.db.models import Task
from app.db.session import get_db

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


@router.get("", response_model=list[TaskListItem])
async def list_tasks(db: AsyncSession = Depends(get_db)) -> list[Task]:
    result = await db.execute(select(Task).order_by(Task.id))
    return list(result.scalars().all())


@router.get("/{task_id}", response_model=TaskDetail)
async def get_task(task_id: int, db: AsyncSession = Depends(get_db)) -> Task:
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if task is None:
        raise HTTPException(status_code=404, detail="Задание не найдено")
    return task
