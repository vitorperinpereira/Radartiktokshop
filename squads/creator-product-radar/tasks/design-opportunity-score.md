---
task: "Design Opportunity Score"
responsavel: "@signal-scoring-architect"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - scoring_dimensions
  - weight_targets
  - classification_rules
Saida: |
  - score_formula
  - normalization_rules
  - explanation_contract
Checklist:
  - "[ ] Confirm scoring dimensions and ranges"
  - "[ ] Define normalization and weighting logic"
  - "[ ] Map explanation fields required by API and dashboard"
  - "[ ] Tie score bands to product recommendations"
---

# *design-opportunity-score

Task generated from squad design blueprint for creator-product-radar.

## Usage

```
@signal-scoring-architect
*design-opportunity-score
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `scoring_dimensions` | string | Yes | scoring dimensions |
| `weight_targets` | string | Yes | weight targets |
| `classification_rules` | string | Yes | classification rules |

## Output

- **score_formula**: score formula
- **normalization_rules**: normalization rules
- **explanation_contract**: explanation contract

## Origin

Confidence: 96%
