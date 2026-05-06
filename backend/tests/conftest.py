import asyncio

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.db.models import Base
from app.sandbox.schema_manager import setup_task_schemas
from app.tasks.seed import seed


@pytest.fixture(scope="session", autouse=True)
def setup_database() -> None:
    async def _run() -> None:
        engine = create_async_engine(settings.trainer_db_url)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        await seed(factory)
        await setup_task_schemas(factory)
        await engine.dispose()

    asyncio.run(_run())
