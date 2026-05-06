from datetime import datetime
from typing import Any

from pydantic import BaseModel


class TaskListItem(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    topic: str
    difficulty: int
    title: str


class TaskDetail(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    topic: str
    difficulty: int
    title: str
    description: str
    schema_setup: str
    check_ordered: bool
    check_columns_strict: bool
    hints: list[str]
    theory: str
    created_at: datetime


class ExecuteResponse(BaseModel):
    columns: list[str]
    rows: list[list[Any]]
    error: str | None


class CheckResponse(BaseModel):
    correct: bool
    message: str
    expected: list[list[Any]]
    got: list[list[Any]]
