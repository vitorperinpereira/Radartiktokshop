# Backlog

Sizing:

- `S`: 1-2 dev-days
- `M`: 3-5 dev-days
- `L`: 5-8 dev-days

## Epic 1 - Foundation

### CPR-001

- Title: Bootstrap Python project with `uv`
- Owner: foundation engineer
- Estimate: `S`
- Dependencies: none
- Output: project metadata, lockfile, base dependency groups

### CPR-002

- Title: Create target repository structure and CLI entrypoint
- Owner: foundation engineer
- Estimate: `S`
- Dependencies: `CPR-001`
- Output: `bin`, `apps`, `services`, `infra`, `tests`, `scripts`

### CPR-003

- Title: Add Docker Compose with PostgreSQL and env baseline
- Owner: foundation engineer
- Estimate: `M`
- Dependencies: `CPR-001`
- Output: local database service, `.env.example`, quickstart commands

### CPR-004

- Title: Add FastAPI and Streamlit skeletons
- Owner: app engineer
- Estimate: `M`
- Dependencies: `CPR-002`, `CPR-003`
- Output: health endpoint, placeholder dashboard, startup commands

## Epic 2 - Persistence and domain

### CPR-005

- Title: Create initial Alembic setup and base migrations
- Owner: backend engineer
- Estimate: `M`
- Dependencies: `CPR-003`
- Output: migration chain for core tables

### CPR-006

- Title: Implement canonical product schema and alias model
- Owner: backend engineer
- Estimate: `M`
- Dependencies: `CPR-005`
- Output: `products`, `product_aliases`, data access layer

### CPR-007

- Title: Implement snapshot, ingestion job, and pipeline run persistence
- Owner: backend engineer
- Estimate: `M`
- Dependencies: `CPR-005`
- Output: lineage tables and repositories

### CPR-008

- Title: Define normalization and deduplication policy in code
- Owner: domain engineer
- Estimate: `L`
- Dependencies: `CPR-006`, `CPR-007`
- Output: canonical key builder, alias matching, conflict handling

## Epic 3 - Source ingestion

### CPR-009

- Title: Implement CSV adapter
- Owner: ingestion engineer
- Estimate: `M`
- Dependencies: `CPR-007`
- Output: typed CSV import contract and ingestion flow

### CPR-010

- Title: Implement JSON snapshot adapter
- Owner: ingestion engineer
- Estimate: `S`
- Dependencies: `CPR-007`
- Output: typed JSON import contract and ingestion flow

### CPR-011

- Title: Implement mock connector and seed datasets
- Owner: ingestion engineer
- Estimate: `M`
- Dependencies: `CPR-009`, `CPR-010`
- Output: `smoke`, `demo_weekly`, and `edge_cases` profiles

## Epic 4 - Scoring pipeline

### CPR-012

- Title: Implement feature extraction worker
- Owner: scoring engineer
- Estimate: `M`
- Dependencies: `CPR-008`, `CPR-011`
- Output: deterministic signal extraction from normalized products

### CPR-013

- Title: Build LangGraph weekly orchestration flow
- Owner: orchestration engineer
- Estimate: `L`
- Dependencies: `CPR-012`
- Output: state graph, retries, run persistence

### CPR-014

- Title: Implement Trend Agent contract and runtime
- Owner: AI engineer
- Estimate: `M`
- Dependencies: `CPR-013`
- Output: structured score and rationale payload

### CPR-015

- Title: Implement Viral Potential Agent contract and runtime
- Owner: AI engineer
- Estimate: `M`
- Dependencies: `CPR-013`
- Output: structured score and rationale payload

### CPR-016

- Title: Implement Creator Accessibility Agent contract and runtime
- Owner: AI engineer
- Estimate: `M`
- Dependencies: `CPR-013`
- Output: structured score and rationale payload

### CPR-017

- Title: Implement score aggregation, class bands, and explainability payload
- Owner: scoring engineer
- Estimate: `M`
- Dependencies: `CPR-014`, `CPR-015`, `CPR-016`
- Output: final score calculation and persistence contract

### CPR-024

- Title: Implement standalone deterministic scoring engine module
- Owner: scoring engineer
- Estimate: `L`
- Dependencies: `CPR-017`
- Output: isolated top-level `scoring/` package with pure factor functions, calibration helpers, and batch scoring tests

## Epic 5 - Report and product surfaces

### CPR-018

- Title: Build ranking, product detail, and report history APIs
- Owner: app engineer
- Estimate: `M`
- Dependencies: `CPR-017`
- Output: read endpoints for weekly output

### CPR-019

- Title: Build Streamlit ranking and product detail views
- Owner: app engineer
- Estimate: `M`
- Dependencies: `CPR-018`
- Output: read-only dashboard with filters and details

### CPR-020

- Title: Implement report builder and export payload
- Owner: reporting engineer
- Estimate: `S`
- Dependencies: `CPR-017`
- Output: weekly ranking summary with hooks and rationale

## Epic 6 - Quality and operations

### CPR-021

- Title: Add lint, typecheck, and test gates
- Owner: foundation engineer
- Estimate: `S`
- Dependencies: `CPR-001`, `CPR-002`
- Output: project quality commands and CI-ready scripts

### CPR-022

- Title: Add integration and smoke coverage for weekly run
- Owner: QA engineer
- Estimate: `L`
- Dependencies: `CPR-018`, `CPR-019`, `CPR-020`
- Output: end-to-end validation using seed data

### CPR-023

- Title: Write local runbook, testing guide, and source governance docs
- Owner: technical writer or lead engineer
- Estimate: `M`
- Dependencies: `CPR-021`, `CPR-022`
- Output: operational documentation for MVP

## Epic 7 - Offline Ranking and Export Utilities

### CPR-025

- Title: Implement standalone ranking service, filters, and report export
- Owner: ranking engineer
- Estimate: `L`
- Dependencies: `CPR-024`
- Output: isolated top-level `ranking/` package with offline ranking generation, JSON/CSV exports, and CLI entrypoint

### CPR-026

- Title: Harden the real Streamlit dashboard read surface and validate its main interactions
- Owner: app engineer
- Estimate: `L`
- Dependencies: `CPR-019`, `CPR-022`
- Output: persisted dashboard landing/history integration, verified Weekly Radar and Product Drilldown interactions, and stronger smoke coverage than simple UI reachability

## Epic 9 - External Ingestion and Signal Synthesis

### CPR-027

- Title: Implement Apify ingestion layer and ProductSignals extraction
- Owner: ingestion engineer
- Estimate: `L`
- Dependencies: `CPR-024`
- Output: isolated top-level `ingestion/` package with Apify client, scrapers, transformers, local JSON cache, and a standalone CLI that emits `ProductSignals`

### CPR-028

- Title: Implement local TikTok OAuth callback bootstrap
- Owner: ingestion engineer
- Estimate: `S`
- Dependencies: `CPR-027`
- Output: TikTok auth-only env loading, local callback endpoint, token cache persistence, and local setup docs for OAuth redirect testing

## Epic 10 - Branding And Design System Documentation

### CPR-029

- Title: Plan branding documentation program with the branding squad
- Owner: brand strategist
- Estimate: `S`
- Dependencies: `CPR-028`
- Output: squad-owned documentation program plan, workstreams, risks, QA gates, and tracked story sequence

### CPR-030

- Title: Define design system documentation architecture and component taxonomy
- Owner: design-system architect
- Estimate: `M`
- Dependencies: `CPR-029`
- Output: documentation structure for foundations, components, adoption matrix, and governance
  - Story link: `1.26`

### CPR-031

- Title: Document priority brand components using Atomic Design
- Owner: component builder
- Estimate: `M`
- Dependencies: `CPR-030`
- Output: first component specs for the hero card, product row, app shell, content card, and landing hero
- Story link: `1.27`

### CPR-032

- Title: Publish cross-surface adoption matrix for React and Python surfaces
- Owner: visual designer
- Estimate: `S`
- Dependencies: `CPR-030`
- Output: alignment guidance for React, HTML templates, Streamlit, and API-facing naming/copy surfaces

### CPR-033

- Title: Finalize branding and design-system QA governance
- Owner: brand QA
- Estimate: `S`
- Dependencies: `CPR-031`, `CPR-032`
- Output: consistency checklist usage, audit evidence, and final PASS/CONCERNS/FAIL gate model
