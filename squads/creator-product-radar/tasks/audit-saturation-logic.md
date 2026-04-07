---
task: "Audit Saturation Logic"
responsavel: "@commerce-signal-analyst"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - saturation_inputs
  - creative_fatigue_signals
  - benchmarking_window
Saida: |
  - saturation_rules
  - risk_flags
  - calibration_notes
Checklist:
  - "[ ] Define early, peak, and saturated stages"
  - "[ ] Map measurable fatigue indicators"
  - "[ ] Align saturation output with score penalties"
  - "[ ] Document edge cases for fast-moving categories"
---

# *audit-saturation-logic

Task generated from squad design blueprint for creator-product-radar.

## Usage

```
@commerce-signal-analyst
*audit-saturation-logic
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `saturation_inputs` | string | Yes | saturation inputs |
| `creative_fatigue_signals` | string | Yes | creative fatigue signals |
| `benchmarking_window` | string | Yes | benchmarking window |

## Output

- **saturation_rules**: saturation rules
- **risk_flags**: risk flags
- **calibration_notes**: calibration notes

## Origin

Confidence: 90%
