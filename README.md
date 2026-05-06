# SQL Trainer

Web-based SQL practice platform. Users write queries against real PostgreSQL; results are compared to reference solutions.

## Quick start

```bash
docker compose up --build -d
```

The `api` service waits for both databases to pass their healthchecks before starting (~15–30 s on first run while Postgres initialises).

## Verify everything works

```bash
# Should return: {"status":"ok","trainer_db":"ok","sandbox_db":"ok"}
curl http://localhost:8000/health
```

PowerShell equivalent:
```powershell
Invoke-RestMethod http://localhost:8000/health
```

## Services

| Service    | Host port | Description                       |
|------------|-----------|-----------------------------------|
| api        | 8000      | FastAPI application               |
| trainer-db | 5433      | Metadata / task database          |
| sandbox-db | 5434      | Isolated DB for user query runs   |

## Credentials

**trainer-db** (`localhost:5433`, database `trainer`)
- Admin user: `trainer_user` / `trainer_pass`

**sandbox-db** (`localhost:5434`, database `sandbox`)
- Admin user: `postgres` / `sandbox_pass`
- Query-execution user: `sandbox_user` / `sandbox_user_pass` (SELECT-only, 5 s timeout)

## Alembic migrations

Run from `backend/` with the stack up:

```bash
cd backend
alembic upgrade head
alembic revision --autogenerate -m "description"
```

## Local development (without Docker)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux
pip install -e ".[dev]"
cp .env.example .env            # adjust URLs if needed
uvicorn app.main:app --reload
```

## Code quality

```bash
cd backend
ruff check app/
ruff format app/
mypy app/
```

## Stop / clean up

```bash
docker compose down        # stop, keep volumes
docker compose down -v     # stop and delete all data
```
