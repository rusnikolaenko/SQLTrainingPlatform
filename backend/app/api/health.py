import asyncpg
from fastapi import APIRouter
from sqlalchemy import text

from app.core.config import settings
from app.db.session import trainer_engine

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    trainer_status = await _check_trainer_db()
    sandbox_status = await _check_sandbox_db()
    overall = "ok" if trainer_status == "ok" and sandbox_status == "ok" else "error"
    return {"status": overall, "trainer_db": trainer_status, "sandbox_db": sandbox_status}


async def _check_trainer_db() -> str:
    try:
        async with trainer_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return "ok"
    except Exception:
        return "error"


async def _check_sandbox_db() -> str:
    try:
        conn = await asyncpg.connect(dsn=settings.sandbox_asyncpg_dsn)
        try:
            await conn.execute("SELECT 1")
        finally:
            await conn.close()
        return "ok"
    except Exception:
        return "error"
