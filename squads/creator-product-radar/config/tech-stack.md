# Tech Stack - Creator Product Radar

## Primary Runtime

- Python 3.12 for API, workers, scoring, and orchestration.
- FastAPI for REST endpoints and OpenAPI documentation.
- LangGraph for analytic orchestration across workers and runtime agents.
- SQLModel or SQLAlchemy with Alembic for persistence and migrations.
- PostgreSQL as the system of record.
- Streamlit for the first dashboard iteration, with room to evolve later.

## Core Python Packages

- `fastapi`
- `uvicorn`
- `sqlmodel`
- `alembic`
- `psycopg[binary]`
- `langgraph`
- `pandas`
- `pydantic-settings`
- `httpx`
- `pytest`

## Supporting Practices

- Docker and Docker Compose for local development parity.
- Seed fixtures and mock adapters for MVP delivery without live platform coupling.
- Structured logging for ingestion jobs, graph execution, and report generation.
- Optional Redis or queueing only after the MVP bottleneck is real.

## Deliberate MVP Choices

- Prefer CSV, JSON snapshots, and mocks before live TikTok Shop connectors.
- Keep frontend scope modest; insight quality matters more than UI complexity.
- Use configuration-driven score weights instead of premature ML infrastructure.
