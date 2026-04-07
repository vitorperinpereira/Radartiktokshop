# Coding Standards - Creator Product Radar

This squad extends the core AIOX standards with domain-specific rules for creator-commerce intelligence.

## Architecture Boundaries

- Keep runtime AI agents separate from squad governance agents.
- Treat external platforms as adapters, never as hard dependencies for the MVP.
- Keep deterministic business logic outside prompt files.
- Every score contribution must be explainable from persisted evidence.
- Prefer simple contracts over orchestration cleverness.

## Backend Rules

- Use small Python modules with explicit input and output schemas.
- Keep HTTP handlers thin; orchestration and scoring belong in services.
- Model source adapters as interfaces with mock, CSV, and JSON implementations.
- Centralize prompt text and agent output contracts in dedicated modules.
- Persist raw snapshots separately from normalized product entities.

## Data and Scoring Rules

- Every signal must specify origin, freshness, and failure mode.
- Deduplication rules must be deterministic and testable.
- Never change score weights without recording the rationale.
- Saturation penalties must be evidence-based, not gut feel.
- Favor rules that keep small and mid-sized creators competitive.

## Report and Content Rules

- Do not ship rankings without a clear textual rationale.
- Content angles must map to product evidence and creator constraints.
- Avoid generic hooks that could fit any product.
- Flag risky claims before they reach reports or dashboard copy.

## Quality Bar

- Add unit tests for scoring math, adapters, normalization, and report builders.
- Add integration tests for the weekly pipeline and seed flows.
- Keep sample fixtures realistic enough to expose ranking edge cases.
- Document every new data source before implementation begins.
