---
task: "Calibrate Score Model"
responsavel: "@signal-scoring-architect"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - weights
  - backtest_samples
  - business_priorities
Saida: |
  - calibrated_weights
  - tradeoffs
  - admin_controls
Checklist:
  - "[ ] Evaluate current weights against target outcomes"
  - "[ ] Record tradeoffs between virality and accessibility"
  - "[ ] Propose admin-tunable configuration surface"
  - "[ ] Define recalibration cadence"
---

# *calibrate-score-model

Task generated from squad design blueprint for creator-product-radar.

## Usage

```
@signal-scoring-architect
*calibrate-score-model
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `weights` | string | Yes | weights |
| `backtest_samples` | string | Yes | backtest samples |
| `business_priorities` | string | Yes | business priorities |

## Output

- **calibrated_weights**: calibrated weights
- **tradeoffs**: tradeoffs
- **admin_controls**: admin controls

## Origin

Confidence: 91%
