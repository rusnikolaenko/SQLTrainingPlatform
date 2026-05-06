import sqlparse
from sqlparse import tokens as T

MAX_QUERY_LENGTH = 2000


class ValidationError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


def _first_meaningful_keyword(stmt: sqlparse.sql.Statement) -> str:
    """Return the first non-whitespace, non-comment keyword token (uppercased)."""
    for token in stmt.flatten():
        if token.is_whitespace:
            continue
        if token.ttype in (T.Comment.Single, T.Comment.Multiline, T.Newline):
            continue
        if token.ttype in (T.Keyword, T.Keyword.DML, T.Keyword.DDL):
            return token.normalized.upper()
        return ""
    return ""


def validate_query(query: str) -> None:
    """
    Raise ValidationError if query is not a single SELECT or WITH…SELECT statement.
    Length is checked here too so callers don't need a separate guard.
    """
    if len(query) > MAX_QUERY_LENGTH:
        raise ValidationError(
            f"Запрос слишком длинный. Максимум — {MAX_QUERY_LENGTH} символов."
        )

    stripped = query.strip()
    if not stripped:
        raise ValidationError("Запрос не может быть пустым.")

    parsed = sqlparse.parse(stripped)
    active = [s for s in parsed if str(s).strip()]

    if len(active) != 1:
        raise ValidationError("Допустим только один SQL-запрос.")

    stmt = active[0]
    stmt_type = stmt.get_type()

    if stmt_type == "SELECT":
        return

    # WITH … SELECT (CTE): sqlparse returns type=None, first keyword is WITH
    if stmt_type is None and _first_meaningful_keyword(stmt) == "WITH":
        return

    raise ValidationError("Разрешены только SELECT-запросы.")
