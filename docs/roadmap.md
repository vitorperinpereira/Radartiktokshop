# Roadmap

## Phase 0 - Planning and scope lock

Goal: freeze MVP scope, core architecture, score model, and acceptance criteria.

Outputs:

- PRD
- architecture baseline
- domain model
- scoring model
- setup plan
- implementation plan
- initial backlog

## Phase 1 - Foundation

Goal: bootstrap the repo and make local execution reliable.

Outputs:

- Python project metadata with `uv`
- base repo structure
- Docker Compose with PostgreSQL
- FastAPI and Streamlit skeletons
- CLI entrypoint
- Alembic setup
- lint, typecheck, and test gates

## Phase 2 - Catalog and ingestion

Goal: ingest, normalize, and persist source data.

Outputs:

- CSV adapter
- JSON adapter
- mock connector
- ingestion job tracking
- canonical product normalization
- alias handling
- deduplication rules
- seed datasets

## Phase 3 - Scoring pipeline

Goal: run weekly scoring from normalized data to explainable outputs.

Outputs:

- feature extraction worker
- LangGraph graph for weekly run
- Trend Agent
- Viral Potential Agent
- Creator Accessibility Agent
- deterministic saturation and revenue heuristics
- score aggregation and classification
- evidence persistence

## Phase 4 - Report and dashboard

Goal: expose ranked output to operators and creators.

Outputs:

- weekly ranking API
- product detail API
- report history API
- Streamlit ranking table
- product detail page
- run and report history views
- report export payload

## Phase 5 - Quality and delivery

Goal: stabilize MVP and prepare it for real weekly usage.

Outputs:

- unit, integration, and smoke coverage
- regression fixtures for scoring and dedup
- runbook and troubleshooting docs
- seed refresh workflow
- release checklist for weekly radar

## Post-MVP

- real platform connectors
- dedicated saturation, commission, and content-angle agents
- queue and retry infrastructure
- richer dashboard UX
- notification and scheduling flows
- admin controls for score weights
- multi-tenant access model
