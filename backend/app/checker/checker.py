from dataclasses import dataclass, field
from typing import Any

from app.db.models import Task
from app.sandbox.executor import QueryResult, execute_query
from app.sandbox.schema_manager import task_schema_name

SUCCESS_MESSAGE = "Верно! Результат совпадает."
ORDER_MESSAGE = "Неверно. Проверьте порядок строк."
COLUMNS_MESSAGE = "Неверно. Не совпадают названия колонок."
MISMATCH_MESSAGE = "Неверно. Результат не совпадает."


@dataclass
class CheckResult:
    correct: bool
    message: str
    expected: list[list[Any]] = field(default_factory=list)
    got: list[list[Any]] = field(default_factory=list)


def _sort_rows(rows: list[list[Any]]) -> list[list[Any]]:
    return sorted(rows, key=lambda row: tuple(repr(value) for value in row))


async def run_solution(task: Task) -> QueryResult:
    return await execute_query(task.solution, schema=task_schema_name(task.id))


async def check(user_query: str, task: Task) -> CheckResult:
    expected = await run_solution(task)
    if expected.error is not None:
        return CheckResult(correct=False, message=expected.error)

    got = await execute_query(user_query, schema=task_schema_name(task.id))
    if got.error is not None:
        return CheckResult(
            correct=False,
            message=got.error,
            expected=expected.rows,
            got=got.rows,
        )

    if task.check_columns_strict and got.columns != expected.columns:
        return CheckResult(
            correct=False,
            message=COLUMNS_MESSAGE,
            expected=expected.rows,
            got=got.rows,
        )

    expected_rows = expected.rows if task.check_ordered else _sort_rows(expected.rows)
    got_rows = got.rows if task.check_ordered else _sort_rows(got.rows)

    if got_rows == expected_rows:
        return CheckResult(
            correct=True,
            message=SUCCESS_MESSAGE,
            expected=expected.rows,
            got=got.rows,
        )

    message = ORDER_MESSAGE if task.check_ordered else MISMATCH_MESSAGE
    return CheckResult(
        correct=False,
        message=message,
        expected=expected.rows,
        got=got.rows,
    )
