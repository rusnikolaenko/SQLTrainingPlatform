import logging

import asyncpg
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import settings
from app.db.models import Task
from app.db.session import AsyncSessionLocal

logger = logging.getLogger(__name__)


def task_schema_name(task_id: int) -> str:
    return f"task_{task_id}"


async def setup_task_schema(task: Task) -> None:
    schema = task_schema_name(task.id)
    conn: asyncpg.Connection[asyncpg.Record] = await asyncpg.connect(
        dsn=settings.sandbox_asyncpg_dsn
    )
    try:
        await conn.execute(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE')
        await conn.execute(f'CREATE SCHEMA "{schema}"')
        await conn.execute(f'SET search_path TO "{schema}"')
        await conn.execute(task.schema_setup)
        await conn.execute(f'GRANT USAGE ON SCHEMA "{schema}" TO sandbox_user')
        await conn.execute(
            f'GRANT SELECT ON ALL TABLES IN SCHEMA "{schema}" TO sandbox_user'
        )
    finally:
        await conn.close()


async def setup_task_schemas(
    session_factory: async_sessionmaker[AsyncSession] = AsyncSessionLocal,
) -> None:
    async with session_factory() as session:
        result = await session.execute(select(Task).order_by(Task.id))
        tasks = list(result.scalars().all())

    for task in tasks:
        try:
            await setup_task_schema(task)
        except asyncpg.PostgresError as exc:
            logger.warning(
                "Failed to set up sandbox schema for task %s: %s", task.id, exc
            )
