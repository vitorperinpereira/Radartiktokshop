# Design System Documentation Architecture

## Purpose

This document defines how the branding squad should structure the design-system documentation layer for Creator Product Radar without claiming implementation that does not yet exist.

It sits below `docs/branding-documentation-plan.md` and above the individual component specs that will be created by later stories.

## Scope

### In scope

- documentation architecture for the design system
- token taxonomy and naming contract
- foundation docs for color, type, spacing, motion, and semantic tokens
- component documentation taxonomy using Atomic Design
- surface adoption guidance for React, HTML templates, Streamlit, and API-facing copy
- QA and governance rules for documentation consistency

### Out of scope

- runtime token extraction into a shared package
- full component implementation or refactor
- visual redesign outside the current repo-backed brand direction
- new product naming beyond the documented brand architecture

## Source Of Truth

- `docs/branding-documentation-plan.md`
- `docs/prd.md`
- `docs/stories/1.21.branding-book-alignment.md`
- `docs/stories/1.22.branding-artifact-suite-alignment.md`
- `docs/stories/1.23.branding-runtime-copy-alignment.md`
- `squads/branding/output/branding-book.md`
- `squads/branding/output/color-system.md`
- `squads/branding/output/type-system.md`
- `squads/branding/output/spacing-system.md`
- `squads/branding/output/motion-system.md`
- `squads/branding/output/token-architecture.md`
- `squads/branding/output/consistency-report.md`
- `squads/branding/output/gate-decision.md`

## Architecture

### Layer 1 - Brand governance

This layer defines the brand story, naming architecture, visual principles, and surface mapping.

Primary document:

- `squads/branding/output/branding-book.md`

### Layer 2 - Foundation documentation

This layer defines the reusable foundation contract for the design system.

Documents:

- `squads/branding/output/color-system.md`
- `squads/branding/output/type-system.md`
- `squads/branding/output/spacing-system.md`
- `squads/branding/output/motion-system.md`
- `squads/branding/output/token-architecture.md`

### Layer 3 - Component documentation

This layer documents UI patterns and their usage contract using Atomic Design.

Recommended hierarchy:

- atoms
- molecules
- organisms
- templates
- pages

Each component spec should cover:

- purpose
- classification
- props
- variants
- tokens consumed
- states
- accessibility
- composition
- usage example
- do and don't guidance

### Layer 4 - Adoption and parity

This layer explains how the documentation should be applied across actual surfaces.

Surfaces:

- public React surfaces
- signed-in React surfaces
- HTML template experiments
- Streamlit read surfaces
- API and CLI-adjacent naming

### Layer 5 - QA and governance

This layer reviews consistency, accessibility, naming drift, and rollout order.

Documents:

- `squads/branding/output/consistency-report.md`
- `squads/branding/output/gate-decision.md`
- `squads/branding/checklists/brand-consistency-checklist.md`

## Token Contract

The documentation should use a three-layer token model.

1. Primitive brand values
2. Semantic product tokens
3. Surface aliases

The contract must keep brand color, destructive color, score color, and surface-specific aliases distinct.

## Component Taxonomy

### Atoms

Small, reusable pieces such as buttons, badges, labels, and icons.

### Molecules

Small combinations of atoms such as score rows, filter chips, and metric blocks.

### Organisms

Larger composite sections such as the ranking hero, sidebar shell, or product detail summary.

### Templates

Page layouts that define structure without final content.

### Pages

Concrete product surfaces with data and real copy.

## Recommended Priority Components

1. Top opportunity hero card
2. Product feed row
3. App shell sidebar
4. Content idea card
5. Landing hero

## Documentation Rules

1. Never describe a runtime implementation as complete unless it exists in the repo.
2. Every foundation rule should cite a real file or surface.
3. Every component spec should distinguish current behavior from future recommendations.
4. Every adoption guideline should say which surface it applies to.
5. Every QA note should separate documentation concerns from repo-wide blockers.

## Delivery Sequence

1. Lock the architecture and taxonomy.
2. Document the priority foundation contracts.
3. Add component specs for the most visible UI patterns.
4. Publish surface adoption guidance.
5. Close the loop with QA and gate decision.
