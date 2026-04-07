---
task: "Draft Weekly Report Brief"
responsavel: "@creator-content-strategist"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - ranking_fields
  - audience_segments
  - report_goals
Saida: |
  - report_outline
  - insight_blocks
  - weekly_narrative
Checklist:
  - "[ ] Define the structure of the weekly ranking report"
  - "[ ] Separate operator and creator-facing insights"
  - "[ ] Specify what must be exported versus displayed"
  - "[ ] Keep justifications concise and actionable"
---

# *draft-weekly-report-brief

Task generated from squad design blueprint for creator-product-radar.

## Usage

```
@creator-content-strategist
*draft-weekly-report-brief
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ranking_fields` | string | Yes | ranking fields |
| `audience_segments` | string | Yes | audience segments |
| `report_goals` | string | Yes | report goals |

## Output

- **report_outline**: report outline
- **insight_blocks**: insight blocks
- **weekly_narrative**: weekly narrative

## Origin

Confidence: 90%
