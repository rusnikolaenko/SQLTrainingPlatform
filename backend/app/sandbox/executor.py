from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

import asyncpg

from app.core.config import settings


@dataclass
class QueryResult:
    columns: list[str] = field(default_factory=list)
    rows: list[list[Any]] = field(default_factory=list)
    error: str | None = None


def _to_json(v: Any) -> Any:
    """Convert an asyncpg value to a JSON-serialisable Python primitive."""
    if v is None or isinstance(v, (bool, int, float, str)):
        return v
    if isinstance(v, Decimal):
        return float(v)
    if isinstance(v, (datetime, date)):
        return v.isoformat()
    if isinstance(v, UUID):
        return str(v)
    return str(v)


async def execute_query(sql: str, schema: str | None = None) -> QueryResult:
    """
    Run *sql* in the sandbox DB as sandbox_user.

    Always sets statement_timeout = 5 s before executing. Returns QueryResult
    with columns/rows on success, or error string on failure — never raises.
    """
    conn: asyncpg.Connection[asyncpg.Record] = await asyncpg.connect(
        dsn=settings.sandbox_user_dsn
    )
    try:
        await conn.execute("SET statement_timeout = '5000'")
        if schema is not None:
            await conn.execute(f'SET search_path TO "{schema}"')
        stmt = await conn.prepare(sql)
        columns = [a.name for a in stmt.get_attributes()]
        records = await stmt.fetch()
        rows: list[list[Any]] = [[_to_json(v) for v in r.values()] for r in records]
        return QueryResult(columns=columns, rows=rows)
    except asyncpg.exceptions.QueryCanceledError:
        return QueryResult(
            error="Превышено время выполнения (5 сек)"
        )
    except asyncpg.PostgresError:
        return QueryResult(error="Ошибка выполнения запроса")
    finally:
        await conn.close()
