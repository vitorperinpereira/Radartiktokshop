# Implementation Plan

## Overview

This plan translates the product brief into an implementable MVP. The project will be built as a CLI-first Python modular monolith with FastAPI, Streamlit, PostgreSQL, and LangGraph.

## Linked specifications

- `docs/prompt tiktokshop.md`
- `docs/prd.md`
- `docs/architecture.md`
- `docs/domain-model.md`
- `docs/scoring-model.md`
- `docs/setup.md`
- `docs/branding-documentation-plan.md`

## Requirements summary

- end-to-end CLI execution for weekly runs
- adapter-based ingestion with CSV, JSON, and mock inputs
- canonical product model with lineage
- explainable weekly score output
- API and dashboard for reading ranked results
- local-first development and deterministic test fixtures

## Technical approach

1. Build a modular monolith and keep domain boundaries at package level.
2. Make deterministic logic first-class and isolate AI logic behind runtime agent contracts.
3. Persist raw, normalized, and scored layers in PostgreSQL.
4. Use LangGraph only for weekly orchestration, not for every system interaction.
5. Make seeds, mocks, and CLI flows available before real connectors.

## Implementation phases

### Phase 1 - Repo foundation

Goal:
Create a runnable local skeleton with consistent tooling.

Deliverables:

- `uv` project setup
- repo tree and base packages
- Docker Compose for Postgres
- FastAPI health endpoint
- Streamlit placeholder
- CLI entrypoint
- Alembic configuration

Estimate:

- `M`

### Phase 2 - Data model and ingestion

Goal:
Persist raw inputs and canonical product entities.

Deliverables:

- initial migrations
- `ingestion_jobs`, `products`, `product_aliases`, `product_snapshots`
- CSV, JSON, and mock adapters
- normalization and dedup logic
- seed data profiles

Estimate:

- `L`

### Phase 3 - Scoring pipeline

Goal:
Generate explainable weekly scores from product data.

Deliverables:

- feature extraction worker
- LangGraph weekly graph
- Trend Agent
- Viral Potential Agent
- Creator Accessibility Agent
- deterministic monetization and saturation heuristics
- score aggregation and class bands

Estimate:

- `L`

### Phase 4 - Report and read surfaces

Goal:
Expose results to operators and creators.

Deliverables:

- ranking endpoints
- product detail endpoints
- report history endpoints
- Streamlit ranking and detail views
- report payload builder

Estimate:

- `M`

### Phase 5 - Quality and release readiness

Goal:
Make the MVP safe to run weekly.

Deliverables:

- unit, integration, and smoke tests
- regression fixtures
- runbook and troubleshooting docs
- final acceptance validation

Estimate:

- `M`

## Dependencies

- Docker for local Postgres
- OpenAI-compatible provider configuration for runtime agents
- dataset seeds or imported CSV/JSON samples
- story-based execution flow required by project governance

## Risks and mitigation

- Weak early data quality: invest early in seeds, lineage, and alias tracking
- Score distrust: persist breakdown, evidence, and config version
- Scope creep: keep MVP to 3 agents and 3 primary runtime workers
- Connector instability: keep adapters and mocks as default development path

## Success criteria

1. Local setup completes with documented commands.
2. A seed dataset can be ingested and scored end-to-end from CLI.
3. Weekly ranking, product detail, and report history can be read through API and dashboard.
4. Every scored product includes explanation, class band, and risk flags.
5. The system can be rerun for the same week without data corruption.

## Branding And Design System Documentation

### Program goal

Create a governed documentation stack for the branding book and design system so future UI and documentation work follows one squad-owned source of truth.

### Documentation phases

#### Phase 6 - Branding governance baseline

Goal:
Consolidate branding governance, naming rules, artifact ownership, and rollout sequencing under the branding squad.

Deliverables:

- `branding-book.md` as parent source of truth
- brand manifesto and identity gap analysis
- explicit squad ownership and QA gates
- tracked planning story and roadmap

Estimate:

- `S`

#### Phase 7 - Design system documentation foundations

Goal:
Turn the existing branding outputs into a coherent design-system documentation foundation.

Deliverables:

- color, type, spacing, motion, and token documentation aligned to one naming contract
- design-system documentation architecture
- cross-surface adoption guidance

Estimate:

- `M`

#### Phase 8 - Component documentation and governance

Goal:
Add the missing operational layer that documents component anatomy, variants, token usage, accessibility, and adoption rules.

Deliverables:

- component taxonomy using Atomic Design
- first component specs for critical product patterns
- QA audit and gate decision for the documentation package

Estimate:

- `M`

#### Phase 9 - Surface adoption and parity

Goal:
Document how the design system is applied across React, templates, Streamlit, and API-adjacent copy surfaces.

Deliverables:

- cross-surface adoption matrix
- parity guidance for naming and copy
- rollout order for visible brand and component usage

Estimate:

- `S`
