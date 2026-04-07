# Product Requirements Document

## Product summary

This product helps TikTok Shop affiliate creators decide what to promote each week through a repeatable, compliance-friendly pipeline. The system produces a ranked weekly radar with a `Creator Opportunity Score` from `0-100`, plus supporting reasoning and suggested content direction.

## Problem

Creators and creator operations teams do not have a reliable, recurring, explainable way to decide which products are worth promoting each week. Most decisions are manual, inconsistent, and overly dependent on noisy signals.

## Goal

Build a CLI-first platform that ingests product data, evaluates opportunity signals, scores products, and publishes a weekly ranked output with enough context for action.

## Users

- Primary: affiliate creators in beginner, intermediate, and advanced stages
- Secondary: internal operator running weekly analysis
- Secondary: agencies or creator support teams reviewing opportunities at scale

## Jobs to be done

- "Tell me what to sell this week."
- "Show me why this product is promising."
- "Signal if the product is too saturated for a small creator."
- "Give me a first content angle I can test quickly."

## Functional requirements

1. Import catalog and snapshot data through CSV, JSON, and mock adapters.
2. Normalize and deduplicate products into canonical entities.
3. Extract deterministic product features and derived signals.
4. Run a weekly LangGraph pipeline with MVP runtime agents:
   - Trend Agent
   - Viral Potential Agent
   - Creator Accessibility Agent
5. Compute a final weighted `Creator Opportunity Score`.
6. Persist raw inputs, normalized entities, signals, scores, evidence, and pipeline runs.
7. Publish a weekly ranking with explanation, classification, saturation risk, and a first content hook.
8. Expose results through a CLI flow, an API, and a simple dashboard.

## Non-functional requirements

1. CLI-first operation must work end-to-end before UI dependency.
2. The system must support local-first development with seeds and mocks.
3. All scoring decisions must be explainable and reproducible.
4. Pipeline runs must be idempotent for the same input snapshot and week.
5. The architecture must allow future connectors and agent expansion without rewriting the core.

## MVP scope

### In scope

- CSV, JSON, and mock ingestion
- PostgreSQL persistence
- FastAPI API
- Streamlit dashboard
- LangGraph orchestration
- 3 MVP runtime agents
- deterministic saturation and monetization heuristics
- weekly report generation

### Deferred

- real TikTok Shop connectors as a mandatory dependency
- dedicated Saturation Agent
- dedicated Commission/Revenue Agent
- dedicated Content Angle Agent
- admin UI for weight tuning
- multi-tenant auth and billing

## Epics

1. Data Intake and Normalization
2. Opportunity Scoring
3. Weekly Insights
4. Pipeline Orchestration
5. Read-only Dashboard
6. Admin and Extensibility

## Representative user stories

1. As an operator, I want to import weekly product datasets so the analysis can run without platform coupling.
2. As a creator, I want a ranked list with score breakdown and reasoning so I can trust the recommendation.
3. As a creator, I want a saturation indicator so I can avoid overcrowded products.
4. As an operator, I want historical runs preserved so I can compare results and debug anomalies.
5. As a creator, I want a first hook or content angle so I can move from insight to execution quickly.

## Core weekly flow

1. Operator runs ingestion through CLI.
2. System stores raw snapshots and canonical products.
3. Feature extraction computes deterministic signals.
4. LangGraph runs the 3 MVP agents.
5. Deterministic scoring aggregates signals into final score and class band.
6. Report builder generates ranking and narrative summary.
7. API and dashboard expose the results for review.
8. Operator validates and publishes the weekly radar.

## Acceptance criteria

1. A weekly run can be executed from CLI using seeded or imported data.
2. Every ranked product has final score, breakdown, evidence, and class label.
3. The top list can be viewed in dashboard and queried through API.
4. Raw data lineage can be traced back to ingestion job and source record.
5. The system can rerun a week without corrupting historical records.

## Success metrics

- Time-to-insight: ranking available within 15 minutes after dataset upload
- Pipeline reliability: at least 95% successful runs on MVP input formats
- Recommendation completeness: 100% ranked products include score and explanation
- Pilot usefulness: at least 70% of pilot creators rate top 10 as actionable
- Ops efficiency: at least 60% reduction in manual weekly curation effort

## Risks and mitigation

- Source instability or compliance risk: keep adapters optional and default to CSV, JSON, and mocks
- Low trust in early scores: expose breakdown, evidence, and weight rationale
- Overengineering: keep MVP to 3 agents, 3 workers, and a read-only dashboard
- Weak deduplication: preserve aliases, snapshots, and regression fixtures
- Drift from CLI-first rule: require operational completeness via CLI before dashboard polish

## Assumptions

- MVP users accept internal or semi-internal tooling before polished SaaS UX
- Weekly cadence is enough for the first version
- Signal quality can start with heuristics and improve through calibration
- Real connectors are not required to validate the initial value proposition
