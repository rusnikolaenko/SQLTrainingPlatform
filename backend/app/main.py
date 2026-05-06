from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.check import router as check_router
from app.api.execute import router as execute_router
from app.api.health import router as health_router
from app.api.tasks import router as tasks_router
from app.sandbox.schema_manager import setup_task_schemas


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    await setup_task_schemas()
    yield


app = FastAPI(title="SQL Trainer API", lifespan=lifespan)

app.include_router(health_router)
app.include_router(tasks_router)
app.include_router(check_router)
app.include_router(execute_router)

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_STATIC_DIR = _PROJECT_ROOT / "frontend" / "static"
if not _STATIC_DIR.exists():
    _STATIC_DIR = Path("/frontend/static")

app.mount("/", StaticFiles(directory=_STATIC_DIR, html=True), name="frontend")
