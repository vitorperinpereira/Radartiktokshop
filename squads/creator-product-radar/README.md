# Creator Product Radar

Domain squad for the SaaS described in [docs/prompt tiktokshop.md](../../docs/prompt%20tiktokshop.md).
It specializes the base AIOX stack for affiliate-commerce intelligence without duplicating the core delivery agents.

## What This Squad Adds

- Evidence-driven signal design for trend, saturation, creator accessibility, and monetization.
- Source governance for CSV, JSON, mock, and future TikTok Shop adapters.
- Catalog normalization rules for canonical products, variants, and deduplication.
- Score model design and evaluation discipline for the Creator Opportunity Score.
- Creator-facing report and content-angle quality controls.

## What Stays In Core AIOX

- `@architect`, `@dev`, `@data-engineer`, `@qa`, `@devops` keep implementation ownership.
- `@pm`, `@po`, `@sm`, `@analyst`, and `@ux-design-expert` keep product, planning, and UX responsibilities.
- This squad governs domain rules, contracts, heuristics, and operating quality for the product.

## Specialized Agents

- `@commerce-signal-analyst`
- `@signal-scoring-architect`
- `@source-governance-engineer`
- `@catalog-normalization-engineer`
- `@creator-content-strategist`

## High-Value Tasks

- `*define-signal-catalog`
- `*design-opportunity-score`
- `*qualify-data-source`
- `*maintain-product-ontology`
- `*evaluate-agent-contracts`
- `*draft-weekly-report-brief`

## Workflows

- `creator-product-radar-mvp.yaml`: turns the brief into domain artifacts and a delivery-ready implementation loop.
- `weekly-radar-cycle.yaml`: governs the weekly analysis and reporting cycle when the product is running.

## Recommended Usage

1. Use `@commerce-signal-analyst` to define the measurable evidence model.
2. Use `@source-governance-engineer` and `@catalog-normalization-engineer` to lock data contracts before coding adapters.
3. Use `@signal-scoring-architect` to finalize scoring, explanation output, and calibration.
4. Use `@creator-content-strategist` to shape report narrative and creator-ready hooks.
5. Hand the approved artifacts to core AIOX agents for implementation.

## Validation

Run:

```bash
node .aiox-core/development/scripts/squad/index.js validate ./squads/creator-product-radar
```

or use the squad creator flow:

```bash
@squad-creator *validate-squad creator-product-radar
```

## License

MIT
