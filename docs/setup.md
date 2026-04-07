# Setup Plan

## Local stack

- Python `3.12`
- `uv` for environment and dependency management
- FastAPI for API surface
- Streamlit for first dashboard
- PostgreSQL `16` via Docker Compose
- SQLAlchemy or SQLModel plus Alembic for persistence and migrations
- LangGraph for weekly pipeline orchestration
- pytest, ruff, and mypy or pyright for quality gates

## Planned local services

- `api`: FastAPI app
- `dashboard`: Streamlit app
- `db`: PostgreSQL

Redis or queue infra is intentionally out of MVP until a real throughput bottleneck appears.

## Environment variables

Create `.env.example` around:

- `APP_ENV`
- `DATABASE_URL`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `OPENAI_API_KEY`
- `MODEL_PROVIDER`
- `LOG_LEVEL`
- `SEED_PROFILE`
- `REPORT_TIMEZONE`

## Bootstrap steps

1. Initialize Python project metadata and lockfile with `uv`.
2. Create repo structure for `apps`, `services`, `infra`, `tests`, and `scripts`.
3. Add Docker Compose for local Postgres.
4. Add FastAPI, Streamlit, LangGraph, db, and test dependencies.
5. Create initial Alembic setup and first migration set.
6. Add a minimal CLI entrypoint in `bin/radar.py`.
7. Add seed scripts for `smoke`, `demo_weekly`, and `edge_cases`.

## Database plan

Initial tables:

- `products`
- `product_aliases`
- `product_snapshots`
- `creators`
- `product_signals`
- `product_scores`
- `content_angles`
- `reports`
- `ingestion_jobs`
- `pipeline_runs`

Migration policy:

- keep seeds outside migrations
- use UTC timestamps everywhere
- preserve raw JSON payloads and explicit lineage

## Test strategy

### Unit

- scoring rules
- normalization and dedup logic
- adapter contracts
- report builders

### Integration

- alembic upgrade
- CSV and JSON ingestion
- LangGraph pipeline with mocks
- API endpoints with Postgres

### Smoke

- local boot via Docker Compose
- seed load
- weekly run
- dashboard availability

## Seed and mock strategy

Profiles:

- `smoke`
- `demo_weekly`
- `edge_cases`

Adapters:

- `csv_adapter`
- `json_snapshot_adapter`
- `mock_connector`

## Operational docs to maintain

- `docs/testing.md`
- `docs/source-governance.md`
- `docs/runbook-local.md`
- `docs/roadmap.md`
