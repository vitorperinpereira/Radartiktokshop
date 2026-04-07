---
task: "Maintain Product Ontology"
responsavel: "@catalog-normalization-engineer"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - raw_catalog_fields
  - variant_patterns
  - category_rules
Saida: |
  - canonical_product_model
  - deduplication_rules
  - taxonomy_decisions
Checklist:
  - "[ ] Define canonical product identity rules"
  - "[ ] Specify alias and variant grouping behavior"
  - "[ ] Document category taxonomy and normalization steps"
  - "[ ] Align snapshot fields with downstream scoring"
---

# *maintain-product-ontology

Task generated from squad design blueprint for creator-product-radar.

## Usage

```
@catalog-normalization-engineer
*maintain-product-ontology
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `raw_catalog_fields` | string | Yes | raw catalog fields |
| `variant_patterns` | string | Yes | variant patterns |
| `category_rules` | string | Yes | category rules |

## Output

- **canonical_product_model**: canonical product model
- **deduplication_rules**: deduplication rules
- **taxonomy_decisions**: taxonomy decisions

## Origin

Confidence: 94%
