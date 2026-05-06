import asyncio
from pathlib import Path
from typing import Any

import yaml
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.db.models import Task

_HERE = Path(__file__).resolve()
TASKS_DATA_DIR = _HERE.parents[3] / "tasks_data"


def _load_yaml_tasks() -> list[dict[str, Any]]:
    tasks: list[dict[str, Any]] = []
    for yaml_file in sorted(TASKS_DATA_DIR.rglob("*.yaml")):
        with open(yaml_file, encoding="utf-8") as f:
            tasks.append(yaml.safe_load(f))
    return tasks


async def seed(
    session_factory: async_sessionmaker[AsyncSession] | None = None,
) -> None:
    if session_factory is None:
        from app.db.session import AsyncSessionLocal

        session_factory = AsyncSessionLocal

    tasks_data = _load_yaml_tasks()

    async with session_factory() as session:
        for data in tasks_data:
            check = data.get("check", {})
            values: dict[str, Any] = {
                "id": data["id"],
                "topic": data["topic"],
                "difficulty": data["difficulty"],
                "title": data["title"],
                "description": data["description"],
                "schema_setup": data["schema_setup"],
                "solution": data["solution"],
                "check_ordered": check.get("ordered", False),
                "check_columns_strict": check.get("columns_strict", True),
                "hints": data.get("hints", []),
                "theory": data.get("theory", ""),
            }
            stmt = (
                pg_insert(Task)
                .values(**values)
                .on_conflict_do_update(
                    index_elements=["id"],
                    set_={k: v for k, v in values.items() if k != "id"},
                )
            )
            await session.execute(stmt)
        await session.commit()

    print(f"Seeded {len(tasks_data)} tasks from {TASKS_DATA_DIR}")


if __name__ == "__main__":
    asyncio.run(seed())
