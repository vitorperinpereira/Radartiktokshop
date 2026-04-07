# Project Tracker

Last update: 2026-03-22

## How to read this file

- `[x]` means the work is implemented in the repository.
- `[ ]` means the work is not fully complete yet.
- When something is only partial, the line keeps `[ ]` and the note says `In progress`.
- Current story files can be in `Review` while still being checked here as implemented.

## Snapshot

- Current phase: repo quality blockers resolved; branding documentation architecture and component specs are underway
- Story files created: 27
- Stories implemented: 27
- Backlog tasks: 33 total
- Backlog tasks completed: 30
- Backlog tasks in progress: 1
- Backlog tasks pending: 3

## Story Status

- [x] Story 1.1 - Foundation Bootstrap
  - Status: `Review`
  - File: `docs/stories/1.1.foundation-bootstrap.md`
  - Scope delivered: repo scaffold, CLI health, FastAPI placeholder, Streamlit placeholder, compose/env, quality wrappers

- [x] Story 1.2 - Initial Persistence Schema
  - Status: `Review`
  - File: `docs/stories/1.2.initial-persistence-schema.md`
  - Scope delivered: ORM base, core tables, Alembic wiring, initial migration, DB bootstrap tests

- [x] Story 1.3 - Bootstrap Ingestion Flow
  - Status: `Review`
  - File: `docs/stories/1.3.bootstrap-ingestion.md`
  - Scope delivered: adapter contract, mock+CSV ingestion, CLI DB upgrade, snapshot persistence, ingestion tests

- [x] Story 1.4 - JSON Ingestion and Alias-Aware Dedup
  - Status: `Review`
  - File: `docs/stories/1.4.json-alias-dedup.md`
  - Scope delivered: JSON adapter, mock profiles, alias-aware matching, profile-based CLI ingestion, repo quality gates green

- [x] Story 1.5 - Weekly Run Persistence Bootstrap
  - Status: `Review`
  - File: `docs/stories/1.5.weekly-run-bootstrap.md`
  - Scope delivered: deterministic feature extraction, persisted pipeline runs, weekly CLI bootstrap, sqlite-backed weekly run tests

- [x] Story 1.6 - LangGraph Weekly Orchestration
  - Status: `Review`
  - File: `docs/stories/1.6.langgraph-weekly-orchestration.md`
  - Scope delivered: typed orchestration state, LangGraph weekly graph, retry-enabled extraction node, weekly-run delegation

- [x] Story 1.7 - Trend Agent Contract and Runtime
  - Status: `Review`
  - File: `docs/stories/1.7.trend-agent-runtime.md`
  - Scope delivered: shared scoring contracts, deterministic Trend Agent runtime, weekly-run Trend node, Trend summary outputs

- [x] Story 1.8 - Viral Potential Agent Contract and Runtime
  - Status: `Review`
  - File: `docs/stories/1.8.viral-potential-agent-runtime.md`
  - Scope delivered: contract metadata extension, deterministic Viral Potential runtime, weekly-run Viral node, Viral summary outputs

- [x] Story 1.9 - Creator Accessibility Agent Contract and Runtime
  - Status: `Review`
  - File: `docs/stories/1.9.creator-accessibility-agent-runtime.md`
  - Scope delivered: deterministic Creator Accessibility runtime, weekly-run Creator node, Creator summary outputs

- [x] Story 1.10 - Score Aggregation, Class Bands, and Explainability Payload
  - Status: `Ready for Review`
  - File: `docs/stories/1.10.score-aggregation-explainability.md`
  - Scope delivered: deterministic final score aggregation, persisted `product_scores`, class bands, explainability payloads, and CLI summary metrics

- [x] Story 1.11 - Read APIs for Weekly Ranking, Product Detail, and History
  - Status: `Ready for Review`
  - File: `docs/stories/1.11.read-apis-ranking-product-history.md`
  - Scope delivered: read-only FastAPI ranking, product detail, pipeline-run history, and report-history endpoints backed by persisted weekly scoring output

- [x] Story 1.12 - Streamlit Ranking and Product Detail Views
  - Status: `Ready for Review`
  - File: `docs/stories/1.12.streamlit-ranking-product-detail.md`
  - Scope delivered: persisted Weekly Radar and Product Drilldown pages, thin dashboard read adapter, and dashboard read-state regression coverage

- [x] Story 1.13 - Report Builder and Export Payload
  - Status: `Ready for Review`
  - File: `docs/stories/1.13.report-builder-export-payload.md`
  - Scope delivered: CLI-first `export-report`, deterministic single-run report payload assembly, persisted `reports` and `content_angles` draft artifacts, and regression coverage for builder/history integration

- [x] Story 1.14 - Integration and Smoke Coverage for Weekly Run
  - Status: `Ready for Review`
  - File: `docs/stories/1.14.integration-and-smoke-coverage-weekly-run.md`
  - Scope delivered: seeded end-to-end smoke coverage through `export-report`, persisted report artifact assertions, and dashboard boot validation on the current read-only operator surface

- [x] Story 1.15 - Local Runbook, Testing Guide, and Source Governance Updates
  - Status: `Ready for Review`
  - File: `docs/stories/1.15.local-runbook-testing-source-governance.md`
  - Scope delivered: updated local runbook, testing guidance, and source governance docs aligned to the implemented CLI/API/dashboard MVP flow and validation coverage

- [x] Story 1.16 - Deterministic Scoring Engine Module
  - Status: `Ready for Review`
  - File: `docs/stories/1.16.deterministic-scoring-engine-module.md`
  - Scope delivered: standalone top-level `scoring/` package with pure factor functions, calibration helpers, batch aggregation, compatibility exports, and focused factor/aggregator test coverage isolated from the live weekly runtime pipeline

- [x] Story 1.17 - Ranking Service, Filters, and Report Export
  - Status: `Ready for Review`
  - File: `docs/stories/1.17.ranking-service-filters-report-export.md`
  - Scope delivered: standalone top-level `ranking/` package that consumes the offline scoring engine, applies synchronized filters, exports weekly rankings in JSON and CSV, and exposes an isolated `python -m ranking.cli` flow without touching live API, DB, dashboard, or runtime control plane

- [x] Story 1.18 - Dashboard Read-Surface Hardening and Interaction Validation
  - Status: `Ready for Review`
  - File: `docs/stories/1.18.dashboard-read-surface-hardening-and-interaction-validation.md`
  - Scope delivered: hardened the real Streamlit dashboard read surface over the existing adapter/read-service path, replaced the Pipeline History mock with persisted backend reads, and proved the main dashboard interactions through stronger smoke/integration coverage without expanding beyond the current MVP

- [x] Story 1.19 - Apify Ingestion Layer and ProductSignals Extraction
  - Status: `Ready for Review`
  - File: `docs/stories/1.19.apify-ingestion-layer-product-signals-extraction.md`
  - Scope delivered: standalone Apify-backed ingestion layer with local JSON cache, transformer pipeline, retry-aware client, and a `python -m ingestion` CLI that emits `ProductSignals`

- [x] Story 1.20 - TikTok OAuth Callback Bootstrap
  - Status: `Ready for Review`
  - File: `docs/stories/1.20.tiktok-oauth-callback-bootstrap.md`
  - Scope delivered: TikTok auth-only env loading, local FastAPI callback exchange path, persisted token-cache bootstrap, and local redirect setup documentation

- [x] Story 1.21 - Branding Book Alignment and Continuation
  - Status: `Ready for Review`
  - File: `docs/stories/1.21.branding-book-alignment.md`
  - Scope delivered: repo-aligned branding book with naming rules, surface mapping, real asset inventory, and rollout priorities for current Vite and Python surfaces

- [x] Story 1.22 - Branding Artifact Suite Alignment
  - Status: `Ready for Review`
  - File: `docs/stories/1.22.branding-artifact-suite-alignment.md`
  - Scope delivered: aligned manifesto, color, type, writing, token, spacing, motion, consistency, gap, and gate documentation grounded in current repo artifacts

- [x] Story 1.23 - Branding Runtime Copy Alignment
  - Status: `Ready for Review`
  - File: `docs/stories/1.23.branding-runtime-copy-alignment.md`
  - Scope delivered: brand-aligned landing, login, dashboard feedback states, and Streamlit root copy across the most visible runtime surfaces

- [x] Story 1.24 - Repo Quality Blocker Fixes
  - Status: `Ready for Review`
  - File: `docs/stories/1.24.repo-quality-blocker-fixes.md`
  - Scope delivered: repo quality gates restored with SQLite-safe migration handling and ranking router compatibility preserved

- [x] Story 1.25 - Branding Documentation Program Planning
  - Status: `Ready for Review`
  - File: `docs/stories/1.25.branding-documentation-program-planning.md`
  - Scope delivered: squad-based program plan, follow-up roadmap, backlog updates, tracker updates, and QA gating model for branding and design-system documentation

- [x] Story 1.26 - Design System Documentation Architecture
  - Status: `Ready for Review`
  - File: `docs/stories/1.26.design-system-documentation-architecture.md`
  - Scope delivered: governed architecture for foundation docs, component taxonomy, token contract, adoption surfaces, and QA rules below the branding book

- [x] Story 1.27 - Core Component Specification Set
  - Status: `Ready for Review`
  - File: `docs/stories/1.27.core-component-specification-set.md`
  - Scope delivered: first-pass component specification plan for the five highest-priority branded UI patterns

## Backlog Task Status

### Epic 1 - Foundation

- [x] CPR-001 - Bootstrap Python project with `uv`
  - Status: Complete
  - Story link: `1.1`

- [x] CPR-002 - Create target repository structure and CLI entrypoint
  - Status: Complete
  - Story link: `1.1`

- [x] CPR-003 - Add Docker Compose with PostgreSQL and env baseline
  - Status: Complete
  - Story link: `1.1`

- [x] CPR-004 - Add FastAPI and Streamlit skeletons
  - Status: Complete
  - Story link: `1.1`

### Epic 2 - Persistence and Domain

- [x] CPR-005 - Create initial Alembic setup and base migrations
  - Status: Complete
  - Story link: `1.2`

- [x] CPR-006 - Implement canonical product schema and alias model
  - Status: Complete
  - Story link: `1.2`, `1.4`

- [x] CPR-007 - Implement snapshot, ingestion job, and pipeline run persistence
  - Status: Complete
  - Story link: `1.2`, `1.3`, `1.5`

- [x] CPR-008 - Define normalization and deduplication policy in code
  - Status: Complete
  - Story link: `1.3`, `1.4`

### Epic 3 - Source Ingestion

- [x] CPR-009 - Implement CSV adapter
  - Status: Complete
  - Story link: `1.3`

- [x] CPR-010 - Implement JSON snapshot adapter
  - Status: Complete
  - Story link: `1.4`

- [x] CPR-011 - Implement mock connector and seed datasets
  - Status: Complete
  - Story link: `1.3`, `1.4`

### Epic 4 - Scoring Pipeline

- [x] CPR-012 - Implement feature extraction worker
  - Status: Complete
  - Story link: `1.5`

- [x] CPR-013 - Build LangGraph weekly orchestration flow
  - Status: Complete
  - Story link: `1.6`

- [x] CPR-014 - Implement Trend Agent contract and runtime
  - Status: Complete
  - Story link: `1.7`

- [x] CPR-015 - Implement Viral Potential Agent contract and runtime
  - Status: Complete
  - Story link: `1.8`

- [x] CPR-016 - Implement Creator Accessibility Agent contract and runtime
  - Status: Complete
  - Story link: `1.9`

- [x] CPR-017 - Implement score aggregation, class bands, and explainability payload
  - Status: Complete
  - Story link: `1.10`

### Epic 5 - Report and Product Surfaces

- [x] CPR-018 - Build ranking, product detail, and report history APIs
  - Status: Complete
  - Story link: `1.11`

- [x] CPR-019 - Build Streamlit ranking and product detail views
  - Status: Complete
  - Story link: `1.12`

- [x] CPR-020 - Implement report builder and export payload
  - Status: Complete
  - Story link: `1.13`

### Epic 6 - Quality and Operations

- [x] CPR-021 - Add lint, typecheck, and test gates
  - Status: Complete
  - Story link: `1.1`, `1.2`

- [x] CPR-022 - Add integration and smoke coverage for weekly run
  - Status: Complete
  - Story link: `1.14`

- [x] CPR-023 - Write local runbook, testing guide, and source governance docs
  - Status: Complete
  - Story link: `1.15`

- [x] CPR-024 - Implement standalone deterministic scoring engine module
  - Status: Complete
  - Story link: `1.16`

### Epic 7 - Offline Ranking and Export Utilities

- [x] CPR-025 - Implement standalone ranking service, filters, and report export
  - Status: Complete
  - Story link: `1.17`

### Epic 8 - Dashboard Integration Hardening

- [x] CPR-026 - Harden the real Streamlit dashboard read surface and validate its main interactions
  - Status: Done
  - Story link: `1.18`

### Epic 9 - External Ingestion and Signal Synthesis

- [x] CPR-027 - Implement Apify ingestion layer and ProductSignals extraction
  - Status: Complete
  - Story link: `1.19`

- [x] CPR-028 - Implement local TikTok OAuth callback bootstrap
  - Status: Complete
  - Story link: `1.20`

### Epic 10 - Branding And Design System Documentation

- [x] CPR-029 - Plan branding documentation program with the branding squad
  - Status: Complete
  - Story link: `1.25`

- [ ] CPR-030 - Define design system documentation architecture and component taxonomy
  - Status: Complete
  - Story link: `1.26`

- [x] CPR-031 - Document priority brand components using Atomic Design
  - Status: Complete
  - Story link: `1.27`

- [ ] CPR-032 - Publish cross-surface adoption matrix for React and Python surfaces
  - Status: Pending
  - Story link: `Planned after 1.26`

- [ ] CPR-033 - Finalize branding and design-system QA governance
  - Status: Pending
  - Story link: `Planned after 1.26`

## Next Up

- [ ] Run `@qa` review for story `1.24`
- [ ] Run `@qa` review for story `1.25`
- [ ] Run `@qa` review for story `1.26`
- [ ] Draft story `1.28` for the cross-surface adoption matrix
