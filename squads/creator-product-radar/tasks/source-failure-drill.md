---
task: "Source Failure Drill"
responsavel: "@source-governance-engineer"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - source_inventory
  - fallback_inputs
  - run_expectations
Saida: |
  - failure_scenarios
  - fallback_runbook
  - resilience_gaps
Checklist:
  - "[ ] Simulate connector unavailability"
  - "[ ] Verify CSV, JSON, and mock fallbacks still work"
  - "[ ] Record degraded-mode expectations"
  - "[ ] List fixes required before production connectors"
---

# *source-failure-drill

Task generated from squad design blueprint for creator-product-radar.

## Usage

```
@source-governance-engineer
*source-failure-drill
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `source_inventory` | string | Yes | source inventory |
| `fallback_inputs` | string | Yes | fallback inputs |
| `run_expectations` | string | Yes | run expectations |

## Output

- **failure_scenarios**: failure scenarios
- **fallback_runbook**: fallback runbook
- **resilience_gaps**: resilience gaps

## Origin

Confidence: 93%
