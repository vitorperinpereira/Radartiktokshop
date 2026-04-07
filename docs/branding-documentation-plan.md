# Branding Documentation Program Plan

## Overview

This plan organizes the Branding & Design System Squad work needed to build and govern the repository's branding book and design system documentation without inventing scope beyond the current repo artifacts.

The program starts from the current documented truth in `squads/branding/output/` and extends it into an operational documentation system that covers brand governance, design foundations, component documentation, cross-surface adoption, and QA review.

## Objectives

1. Keep `squads/branding/output/branding-book.md` as the parent source of truth for naming, positioning, visual principles, and surface mapping.
2. Formalize the design system documentation stack so foundation guidance, component specs, and adoption rules follow one contract.
3. Prevent documentation drift between React, HTML template, Streamlit, API, and repo-facing naming.
4. Distinguish clearly between current implementation and target direction in every branding or design-system artifact.
5. Create a story-driven execution path for the branding squad that is traceable in the same way as the rest of the project.

## Source Of Truth

- `docs/prd.md`
- `docs/stories/1.21.branding-book-alignment.md`
- `docs/stories/1.22.branding-artifact-suite-alignment.md`
- `docs/stories/1.23.branding-runtime-copy-alignment.md`
- `squads/branding/squad.yaml`
- `squads/branding/output/branding-book.md`
- `squads/branding/output/brand-manifesto.md`
- `squads/branding/output/color-system.md`
- `squads/branding/output/type-system.md`
- `squads/branding/output/spacing-system.md`
- `squads/branding/output/motion-system.md`
- `squads/branding/output/token-architecture.md`
- `squads/branding/output/ux-writing-guide.md`
- `squads/branding/output/consistency-report.md`
- `squads/branding/output/identity-gap-analysis.md`
- `squads/branding/output/gate-decision.md`

## Squad Model

### Brand strategist

- Owns naming governance, positioning, manifesto, and brand principles
- Approves changes to brand architecture and narrative
- Ensures the repo keeps one product story across surfaces

### Design-system architect

- Owns token taxonomy, component documentation structure, and atomic hierarchy
- Aligns foundation docs with implementation constraints in the repo
- Defines adoption rules for React, templates, and Python read surfaces

### Specialists

- `color-specialist`: color semantics, score bands, contrast rules
- `typography-lead`: type roles, scale, future font rollout guardrails
- `motion-designer`: timing, transitions, reduced-motion rules
- `content-designer`: UX writing guide and empty-state language
- `visual-designer`: surface patterns and visual consistency
- `component-builder`: component anatomy, variants, and usage contracts

### Brand QA

- Runs consistency, accessibility, and source-of-truth checks
- Issues `PASS`, `CONCERNS`, or `FAIL` decisions for the documentation package

## Program Scope

### In scope

- Branding book governance and maintenance
- Design foundation documentation
- Component documentation templates and first component specs
- Cross-surface naming and adoption matrix
- QA checklist and review flow for branding and design-system artifacts

### Out of scope

- Full token extraction into runtime packages
- Full component implementation or refactor
- Rebranding the product beyond the repo-backed naming already documented
- Introducing new brand assets or surface names without repo evidence

## Workstreams

### Workstream 1 - Brand governance baseline

Goal:
Lock the brand architecture, narrative, and artifact ownership model.

Primary owners:
- `brand-strategist`
- `content-designer`
- `brand-qa`

Deliverables:
- consolidated program brief
- maintained `branding-book.md`
- maintained `brand-manifesto.md`
- maintained `identity-gap-analysis.md`

Definition of done:
- naming rules are explicit for repo, product, workspace, and short UI brand
- every document points back to real repo surfaces
- current state and target direction are separated clearly

### Workstream 2 - Design foundations contract

Goal:
Turn the current color, type, spacing, motion, and token guidance into one coherent foundation stack.

Primary owners:
- `design-system-architect`
- `color-specialist`
- `typography-lead`
- `motion-designer`
- `brand-qa`

Deliverables:
- maintained `color-system.md`
- maintained `type-system.md`
- maintained `spacing-system.md`
- maintained `motion-system.md`
- maintained `token-architecture.md`

Definition of done:
- token naming is consistent across all foundation docs
- destructive, score, and brand semantics are documented without claiming shipped extraction
- guidance references real files such as `frontend/tailwind.config.js` and `frontend/src/index.css`

### Workstream 3 - Component documentation layer

Goal:
Add the missing operational layer between foundation docs and UI implementation.

Primary owners:
- `design-system-architect`
- `component-builder`
- `visual-designer`
- `brand-qa`

Deliverables:
- component documentation taxonomy using Atomic Design
- component spec workflow based on `squads/branding/templates/component-spec-template.md`
- first component specs for the most visible product patterns

Priority component set:
- top opportunity hero card
- product feed row
- app shell sidebar
- content idea card
- landing hero

Definition of done:
- each component spec documents purpose, anatomy, variants, states, tokens consumed, responsive behavior, and accessibility notes
- component docs distinguish implemented patterns from future recommendations

### Workstream 4 - Cross-surface adoption and parity

Goal:
Document how the branding and design-system contract should be adopted across React, templates, Streamlit, and API-adjacent text surfaces.

Primary owners:
- `design-system-architect`
- `visual-designer`
- `content-designer`
- `brand-strategist`

Deliverables:
- surface adoption matrix
- parity rules for React and Python read surfaces
- rollout order for naming, copy, and foundation adoption

Definition of done:
- adoption guidance is explicit per surface
- the plan identifies what can stay formal and what must align to workspace/UI naming
- drift risks are documented with mitigations

### Workstream 5 - QA governance and release gate

Goal:
Make the documentation package reviewable, repeatable, and safe against drift.

Primary owners:
- `brand-qa`
- `brand-strategist`
- `design-system-architect`

Deliverables:
- maintained `consistency-report.md`
- maintained `gate-decision.md`
- updated checklist usage from `squads/branding/checklists/brand-consistency-checklist.md`

Definition of done:
- QA uses explicit gates for source-of-truth, brand alignment, design-system integrity, runtime consistency, and repo quality disclosure
- review outputs always record repo blockers separately from documentation quality

## Delivery Sequence

1. Confirm the brand governance baseline from stories `1.21` to `1.23`.
2. Maintain the foundation docs as one coherent design-system contract.
3. Add the component documentation layer using Atomic Design.
4. Publish the cross-surface adoption matrix and rollout guidance.
5. Run QA audit and issue the program gate decision.

## Planned Story Breakdown

### Story 1.25

- Program planning and squad-based documentation roadmap

### Story 1.26

- Design system documentation architecture and component taxonomy

### Story 1.27

- Core component specification set for priority brand patterns

### Story 1.28

- Cross-surface adoption matrix for React, templates, Streamlit, and API-facing copy

### Story 1.29

- Branding and design-system QA governance finalization

## Risks

- Naming drift returns across repo, product, workspace, and short brand labels
- Foundation docs evolve separately and contradict the parent branding book
- Component documentation is skipped, leaving the design system as passive guidance only
- Future-state recommendations are documented as if already implemented
- Repo-wide lint, typecheck, and test blockers obscure the quality signal of the documentation program

## QA Gates

1. `Source-of-truth gate`: no invented surfaces, assets, or implementation paths
2. `Brand alignment gate`: all artifacts remain subordinate to the branding book
3. `Design-system integrity gate`: color, type, spacing, motion, and token docs use one contract
4. `Runtime consistency gate`: visible product copy and surface naming stay aligned
5. `Repo quality disclosure gate`: `npm run lint`, `npm run typecheck`, and `npm test` are recorded even when blockers are inherited

## Success Criteria

1. The repo has one documented branding program plan tied to squad ownership.
2. The branding book and design-system docs are organized as a governed documentation stack.
3. Future work on component docs and adoption can start from tracked stories instead of ad hoc edits.
4. QA can evaluate documentation quality separately from unrelated repo blockers.
