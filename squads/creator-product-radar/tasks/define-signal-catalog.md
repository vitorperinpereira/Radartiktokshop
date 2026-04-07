---
task: "Define Signal Catalog"
responsavel: "@commerce-signal-analyst"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - market_questions
  - source_constraints
  - stakeholder_goals
Saida: |
  - signal_catalog
  - signal_priorities
  - gap_notes
Checklist:
  - "[ ] Extract ranking questions from the product brief"
  - "[ ] Map each question to objective product signals"
  - "[ ] Separate mandatory signals from optional enrichments"
  - "[ ] Flag gaps that require mock or pluggable adapters"
---

# *define-signal-catalog

Task generated from squad design blueprint for creator-product-radar.

## Usage

```
@commerce-signal-analyst
*define-signal-catalog
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `market_questions` | string | Yes | market questions |
| `source_constraints` | string | Yes | source constraints |
| `stakeholder_goals` | string | Yes | stakeholder goals |

## Output

- **signal_catalog**: signal catalog
- **signal_priorities**: signal priorities
- **gap_notes**: gap notes

## Origin

Confidence: 94%
