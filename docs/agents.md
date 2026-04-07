# Planning and Runtime Agents

## Planning agents used for project definition

The planning package is based on:

- `aiox-master` as orchestration layer
- core AIOX roles for product, architecture, engineering, and QA governance
- `creator-product-radar` squad for domain-specific planning

## Domain planning responsibilities

### `commerce-signal-analyst`

- defines signal quality expectations
- helps shape trend and opportunity factors

### `signal-scoring-architect`

- owns score structure, explainability, and calibration logic

### `source-governance-engineer`

- defines adapter contracts, compliance boundaries, and source lineage rules

### `catalog-normalization-engineer`

- defines canonical product identity, alias handling, and dedup logic

### `creator-content-strategist`

- shapes weekly report framing and first content-angle output

## MVP runtime analysis agents

### `Trend Agent`

- interprets momentum and signal persistence
- returns structured reasoning and a normalized score

### `Viral Potential Agent`

- estimates demo and hook potential
- returns structured reasoning and a normalized score

### `Creator Accessibility Agent`

- evaluates whether a smaller creator can realistically promote the item
- returns structured reasoning and a normalized score

## Deferred runtime agents

- `Saturation Agent`
- `Commission/Revenue Agent`
- `Content Angle Agent`

These should stay out of the first implementation unless a real gap appears in MVP scoring quality.

## Deterministic workers

### `product_ingestion_worker`

- loads CSV, JSON, or mock data
- writes ingestion jobs and raw snapshots

### `feature_extraction_worker`

- computes normalized fields and deterministic features
- prepares state for runtime agents

### `score_aggregation_worker`

- assembles deterministic sub-scores, penalties, and class bands
- persists final explainable score output

### `report_builder_worker`

- assembles weekly ranking, explanations, and export payloads

## Ownership boundaries

1. Runtime agents interpret ambiguous or qualitative signals.
2. Workers perform deterministic transforms and persistence.
3. Final score assembly stays deterministic.
4. Dashboard and API only read and present stored outputs.
5. Source adapters must conform to a common typed contract before entering the pipeline.
