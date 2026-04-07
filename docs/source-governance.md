# Source Governance

## Intent

The MVP must remain operable with local artifacts and deterministic adapters. Source governance exists to ensure every weekly run is traceable, repeatable, and safe to validate without depending on live platform access.

## Current supported source modes

Operator-facing source entrypoints currently supported in the repo:

- `ingest-csv`
- `ingest-json`
- `ingest-mock`

Backed source modes:

- `csv`
- `json`
- `mock`

Live connectors are not required for the current MVP and must not become a hidden dependency for local validation.

## Seed and local fixture policy

Built-in mock profiles:

- `smoke`
- `demo_weekly`
- `edge_cases`

Governance expectations:

1. `smoke` remains the smallest reliable path for CLI, integration, and release-smoke validation.
2. `demo_weekly` is appropriate for richer manual inspection of ranking, detail, and report surfaces.
3. `edge_cases` is reserved for awkward or degraded inputs that should exercise validation and fallback behavior.
4. Seed profiles are first-class local sources, not temporary test hacks.

## Governance rules

1. Every ingestion must flow through an adapter and create an `ingestion_job`.
2. Adapters may not bypass normalization, lineage tracking, or persistence just because the input is local or mock-driven.
3. Every imported record must preserve a raw payload or equivalent raw trace in persistence.
4. Ambiguous, partial, or weak source data should reduce confidence through validation issues, reasoning, or downstream risk flags rather than silently disappearing.
5. Source-specific behavior must remain visible through persisted metadata, not hidden inside one-off scripts or undocumented shortcuts.

## Adapter contract

Every adapter output is expected to provide:

- source metadata
- external record id when available
- normalized candidate fields
- source timestamp or capture time
- raw payload
- validation issues

This keeps CSV, JSON, and mock inputs interchangeable at the ingestion boundary.

## Lineage expectations

The current lineage chain should remain intact:

1. adapter input
2. `ingestion_jobs`
3. `product_snapshots`
4. normalized `products` and aliases
5. derived `product_signals`
6. weekly `product_scores`
7. `reports` and related read surfaces

No source mode should bypass this chain for convenience.

## Fallback policy

1. Prefer stable local fixtures for development, smoke validation, and troubleshooting.
2. If a non-local source ever becomes unreliable, the weekly cycle must still be runnable with CSV, JSON, or mock data.
3. Source freshness and context should remain visible through persisted snapshot or report metadata.
4. Report export and dashboard inspection must be able to operate on persisted data produced from local sources alone.

## Compliance posture

- keep source coupling loose
- preserve auditable lineage
- keep CLI-first validation possible without remote dependencies
- avoid mandatory live-platform assumptions in docs, tests, or runbooks
