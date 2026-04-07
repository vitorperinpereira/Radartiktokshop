---
task: "Qualify Data Source"
responsavel: "@source-governance-engineer"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - source_list
  - compliance_constraints
  - mvp_data_strategy
Saida: |
  - source_decision
  - adapter_contracts
  - fallback_modes
Checklist:
  - "[ ] Separate official, mock, and imported data paths"
  - "[ ] Define adapter interfaces and payload schemas"
  - "[ ] Document rate-limit and compliance boundaries"
  - "[ ] Specify graceful degradation rules"
---

# *qualify-data-source

Task generated from squad design blueprint for creator-product-radar.

## Usage

```
@source-governance-engineer
*qualify-data-source
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `source_list` | string | Yes | source list |
| `compliance_constraints` | string | Yes | compliance constraints |
| `mvp_data_strategy` | string | Yes | mvp data strategy |

## Output

- **source_decision**: source decision
- **adapter_contracts**: adapter contracts
- **fallback_modes**: fallback modes

## Origin

Confidence: 95%
