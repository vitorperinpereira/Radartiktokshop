# Testing Strategy

## Goals

- validate deterministic scoring and explainability behavior
- keep ingestion, normalization, and persistence stable
- prove the CLI-first weekly flow works end-to-end on local seed data
- confirm API, dashboard, and report export remain downstream read surfaces over persisted output

## Primary commands

Project-wide validation:

```powershell
npm run lint
npm run typecheck
npm test
npm run build
```

Focused execution:

```powershell
python -m uv run --cache-dir .uv-cache --frozen --no-sync pytest -q tests/unit
python -m uv run --cache-dir .uv-cache --frozen --no-sync pytest -q tests/integration
python -m uv run --cache-dir .uv-cache --frozen --no-sync pytest -q tests/smoke
```

## Current coverage map

### Unit

Unit coverage focuses on deterministic or transformation-heavy code paths:

- score aggregation, class bands, and explainability payloads
- adapter schema validation and mock profile behavior
- canonical key generation and dedup helpers
- report builder payload formatting
- dashboard read-adapter shaping and empty/error handling

Representative files:

- `tests/unit/test_score_aggregation.py`
- `tests/unit/test_mock_adapter.py`
- `tests/unit/test_report_builder.py`
- `tests/unit/test_dashboard_read_adapter.py`

### Integration

Integration coverage exercises persisted behavior across the current services:

- database bootstrap and schema availability
- ingestion service writes
- weekly graph and weekly run orchestration
- ranking, product detail, pipeline history, and report history reads
- report export persistence and latest-run resolution

Representative files:

- `tests/integration/test_db_bootstrap.py`
- `tests/integration/test_ingestion_service.py`
- `tests/integration/test_weekly_graph.py`
- `tests/integration/test_weekly_run_service.py`
- `tests/integration/test_api_read_endpoints.py`
- `tests/integration/test_report_builder.py`

### Smoke

Smoke validation stays CLI-first and local-first. The active seeded smoke path now covers:

1. `db-upgrade`
2. `ingest-mock --profile smoke --count 2`
3. `weekly-run --profile smoke --week-start 2026-03-09`
4. `export-report --week-start 2026-03-09 --limit 2`
5. dashboard boot via `serve-dashboard`

The smoke test also verifies persisted `reports` and `content_angles` artifacts after export.

Representative files:

- `tests/smoke/test_cli_health.py`
- `tests/smoke/test_cli_weekly_run.py`

## Seed profiles

The repository currently supports these built-in local profiles:

- `smoke`: minimal seeded path for validation and release-smoke coverage
- `demo_weekly`: broader local fixture set for richer manual testing
- `edge_cases`: regression-oriented fixture set for awkward or incomplete inputs

Use the seed profiles through:

```powershell
npm run cli -- ingest-mock --profile smoke --count 2
```

## Validation boundaries

- CLI remains the primary acceptance path.
- API and dashboard validations must consume persisted data produced by the CLI flow.
- Tests should reuse current fixtures and seed profiles before introducing new validation assets.
- Coverage must not invent live connectors, publication workflow, or remote dependencies.

## Failure and empty-path expectations

Current validation explicitly covers:

- weekly-run failure when no completed ingestion jobs exist
- empty ranking and history reads on a clean database
- product-detail not-found behavior
- report export failure when no completed pipeline runs exist
- dashboard read-adapter empty and error paths

## Release gates

Minimum local release-readiness checks:

1. `npm run lint`
2. `npm run typecheck`
3. `npm test`
4. `npm run build`
5. seeded smoke path through `export-report` and dashboard reachability
