from fastapi import APIRouter
from pydantic import BaseModel

from app.api.schemas import ExecuteResponse
from app.sandbox.executor import execute_query
from app.sandbox.schema_manager import task_schema_name
from app.sandbox.validator import ValidationError, validate_query

router = APIRouter(prefix="/api/v1", tags=["execute"])


class ExecuteRequest(BaseModel):
    query: str
    task_id: int | None = None


@router.post("/execute", response_model=ExecuteResponse)
async def execute(body: ExecuteRequest) -> ExecuteResponse:
    try:
        validate_query(body.query)
    except ValidationError as exc:
        return ExecuteResponse(columns=[], rows=[], error=exc.message)

    schema = task_schema_name(body.task_id) if body.task_id is not None else None
    result = await execute_query(body.query, schema=schema)
    return ExecuteResponse(columns=result.columns, rows=result.rows, error=result.error)
