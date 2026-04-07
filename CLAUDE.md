# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Bootstrap (first time)
python -m uv sync --cache-dir .uv-cache --all-groups

# Database
docker compose up -d db                                  # Start PostgreSQL
uv run python -m bin.radar db-upgrade                   # Apply Alembic migrations

# CLI (primary control plane)
uv run python -m bin.radar health                       # Health check
uv run python -m bin.radar ingest-mock --profile smoke  # Ingest mock data
uv run python -m bin.radar ingest-csv --file data.csv   # Ingest from CSV
uv run python -m bin.radar ingest-json --file data.json # Ingest from JSON
uv run python -m bin.radar ingest-apify --keywords "led strip,massager"
uv run python -m bin.radar weekly-run                   # Run the pipeline
uv run python -m bin.radar export-report --limit 10     # Export weekly report

# Surfaces
uv run uvicorn apps.api.main:app --reload --port 8000   # FastAPI at :8000
uv run python -m bin.radar serve-dashboard              # Streamlit at :8501

# Code quality
uv run ruff check apps bin services scoring ranking ingestion tests
uv run ruff format .
uv run mypy apps bin services scoring ranking ingestion tests

# Tests
uv run pytest -q                                        # All tests
uv run pytest tests/unit/ -q                            # Unit tests only
uv run pytest tests/smoke/ -q                           # Smoke tests
uv run pytest tests/integration/ -q                     # Integration tests (needs DB)
uv run pytest tests/test_radar_cli.py -q                # Single test file
```

## Architecture

Modular Python monolith with three surfaces: CLI (primary), FastAPI, and Streamlit. The weekly analysis pipeline is the only agentic part; all other logic (ingestion, scoring, persistence, reports) is deterministic.

**Data flow:**

```
Source Adapters → Ingestion/Normalization → Feature Extraction
→ LangGraph Agents → Deterministic Scoring → PostgreSQL
→ Report Builder / FastAPI / Streamlit
```

### Key layers

| Layer | Path | Responsibility |
|-------|------|----------------|
| CLI entrypoint | `bin/radar.py` | All commands (ingest, run, report, serve) |
| FastAPI | `apps/api/` | Health, jobs, products, rankings, reports endpoints |
| Streamlit | `apps/dashboard/` | Read-only ranking and report explorer |
| Ingestion | `services/ingestion/` | Adapters (CSV/JSON/mock/Apify), normalization, dedup |
| Orchestration | `services/orchestration/` | LangGraph graph definition and weekly run coordinator |
| AI Agents | `services/agents/` | Prompts, contracts, runtime wrappers (signal interpretation only) |
| Scoring | `services/scoring/` | Weighted scoring policies, heuristics, explainability |
| Reporting | `services/reporting/` | Weekly report generation and export |
| Shared | `services/shared/` | Config (`AppSettings`), DB session, logging |
| Standalone scoring | `scoring/` + `ranking/` | Pure math functions (factors, calibration, aggregation) |
| Raw ingestion | `ingestion/` | Apify client, TikTok scrapers, local cache |
| DB migrations | `infra/migrations/` | Alembic migration files |

### Settings

`AppSettings` in `services/shared/config.py` loads from `.env`. Key vars: `DATABASE_URL`, `OPENAI_API_KEY`, `OPENAI_MODEL`, `APIFY_TOKEN`, `INGESTION_KEYWORDS`. Copy `.env.example` to `.env` before running.

### LangGraph pipeline

`services/orchestration/graphs/weekly_graph.py` defines the weekly run graph. `services/orchestration/weekly_run.py` bootstraps it: creates a `PipelineRun` record, invokes the graph, and persists the final state. AI agents interpret signals only — final score math is deterministic in `scoring/`.

### Scoring model

Four pure factor functions in `scoring/factors.py`:
- `f_trend` — momentum (exponential saturation)
- `f_revenue` — revenue potential (square-root normalization)
- `f_competition` — creator accessibility (inverted logistic)
- `f_viral` — content ease (weighted linear composite: demo×0.4, visual×0.35, hook×0.25)

### Test structure

- `tests/unit/` — pure logic, no DB
- `tests/smoke/` — fast end-to-end CLI checks with mock data
- `tests/integration/` — require a running PostgreSQL instance
