# Local Runbook

## Purpose

This runbook documents the current CLI-first MVP flow that exists in the repository today:

1. bootstrap dependencies and storage
2. ingest a local dataset or seed profile
3. execute a weekly run
4. inspect persisted read surfaces
5. export the weekly report payload

The default operator path uses local Postgres via Docker Compose. The smoke path can use an isolated sqlite database through `DATABASE_URL`.

## Prerequisites

- Python and the project virtual environment managed through `uv`
- Docker Desktop or equivalent local Docker runtime for the default Postgres flow
- repository dependencies synced with `npm run bootstrap`
- `.env` aligned with `.env.example` when using the default Postgres setup

## Bootstrap

### Default local Postgres flow

1. Sync dependencies:

```powershell
npm run bootstrap
```

2. Start Postgres:

```powershell
npm run db:up
```

3. Apply migrations:

```powershell
npm run cli -- db-upgrade
```

4. Confirm CLI health and important paths:

```powershell
npm run cli -- health
npm run cli -- paths
```

### Isolated sqlite smoke flow

Use this when validating the weekly pipeline without touching the default Postgres database.

```powershell
$env:DATABASE_URL = "sqlite+pysqlite:///./.tmp/manual-smoke.sqlite3"
npm run cli -- db-upgrade
```

If the `.tmp` file already exists and you want a clean run, remove it before `db-upgrade`.

## Weekly demo run

### Seeded CLI-first path

1. Ingest the built-in smoke profile:

```powershell
npm run cli -- ingest-mock --profile smoke --count 2
```

2. Execute the weekly pipeline for a fixed week:

```powershell
npm run cli -- weekly-run --profile smoke --week-start 2026-03-09
```

3. Export the persisted draft report payload:

```powershell
npm run cli -- export-report --week-start 2026-03-09 --limit 2
```

Expected outcome:

- `weekly-run` returns structured JSON with `status=completed`
- `export-report` returns structured JSON with `status=draft`
- the exported payload includes `report_version=report-mvp-v1`

### Alternative ingestion paths

Use these when validating adapter behavior instead of seeds:

```powershell
npm run cli -- ingest-csv --file path\to\catalog.csv
npm run cli -- ingest-json --file path\to\snapshots.json
```

## Persisted read inspection

### API surface

Start the API:

```powershell
npm run api
```

Key read endpoints:

- `GET /rankings`
- `GET /products/{product_id}`
- `GET /history/pipeline-runs`
- `GET /history/reports`
- `GET /auth/tiktok/callback`

Useful checks after a seeded run:

- `/rankings` returns the latest scored week by default
- `/products/{product_id}` returns score breakdown and latest snapshot metadata
- `/history/reports` returns the generated draft payload from `export-report`

### TikTok Shop OAuth callback

Use this when you need to authorize the TikTok Shop app locally and persist the token cache used by `python -m ingestion`:

1. Set `TIKTOK_APP_KEY`, `TIKTOK_APP_SECRET`, and `TIKTOK_OAUTH_STATE` in `.env`.
2. Start the API with `npm run api`.
3. Register this redirect URI in the TikTok Shop app settings:

```text
http://localhost:8000/auth/tiktok/callback
```

4. Configure the same `state` value in the TikTok Shop app and in local `.env`.

4. Complete the provider authorization flow in the browser.

Expected outcome:

- the callback exchanges `code` or `auth_code`
- the local cache file is written to `.cache/auth/tiktok_token.json` unless `TIKTOK_TOKEN_CACHE_FILE` overrides it
- the browser shows a local success page after the token is saved

### Dashboard surface

Start the read-only Streamlit dashboard:

```powershell
npm run cli -- serve-dashboard --port 8501
```

The current dashboard entrypoint is `apps/dashboard/app.py`. It reads persisted ranking data and points operators to the Streamlit multipage sidebar for Weekly Radar, Product Drilldown, and Pipeline History.

## Reset local environment

### Postgres-backed flow

```powershell
npm run db:down
npm run db:up
npm run cli -- db-upgrade
```

Re-run ingestion and weekly execution after the database is reset.

### Sqlite-backed smoke flow

Remove the sqlite file you used for validation, then run `db-upgrade` again before ingesting new records.

## Troubleshooting

### Database connection issues

- confirm `DATABASE_URL` points to the expected Postgres or sqlite target
- rerun `npm run cli -- db-upgrade` before ingestion if the schema is missing
- use `npm run cli -- health` to confirm the CLI surface sees the active settings

### Migration drift

- rerun `npm run cli -- db-upgrade`
- if using Postgres, reset the local container and reapply migrations
- if using sqlite smoke files, recreate the `.tmp` database from scratch

### Weekly run fails before scoring

Common cause:

- no completed ingestion jobs exist for the selected database

Recovery:

1. run `ingest-mock`, `ingest-csv`, or `ingest-json`
2. rerun `weekly-run`

### Empty ranking or product detail

- confirm the weekly run completed successfully
- confirm you are reading the same database that received the ingest and weekly run
- check `/history/pipeline-runs` and `/history/reports` to verify persisted artifacts exist

### Dashboard does not boot or reads no data

- verify `apps/dashboard/app.py` exists and `serve-dashboard` is pointed at it
- confirm the API/database settings visible to Streamlit match the database used for the weekly run
- if the dashboard starts but shows no ranking, rerun the seeded CLI path and refresh

### Report export errors

- `export-report` requires a completed pipeline run in the active database
- use `--week-start` to target a known scored week
- use `--run-id` when you need one exact completed run instead of latest-run default behavior

## Logs and artifacts to inspect

- CLI JSON output from `db-upgrade`, `ingest-*`, `weekly-run`, and `export-report`
- persisted `pipeline_runs` history via `/history/pipeline-runs`
- persisted `reports` history via `/history/reports`
- Streamlit console output from `serve-dashboard`
