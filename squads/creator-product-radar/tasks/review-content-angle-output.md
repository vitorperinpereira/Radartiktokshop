---
task: "Review Content Angle Output"
responsavel: "@creator-content-strategist"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - product_profile
  - opportunity_score
  - risk_flags
Saida: |
  - hooks
  - content_angles
  - short_script_briefs
Checklist:
  - "[ ] Review the product signals and constraints"
  - "[ ] Produce hooks for small and mid-sized creators"
  - "[ ] Tie each angle to a concrete product trigger"
  - "[ ] Flag claims that need compliance review"
---

# *review-content-angle-output

Task generated from squad design blueprint for creator-product-radar.

## Usage

```
@creator-content-strategist
*review-content-angle-output
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `product_profile` | string | Yes | product profile |
| `opportunity_score` | string | Yes | opportunity score |
| `risk_flags` | string | Yes | risk flags |

## Output

- **hooks**: hooks
- **content_angles**: content angles
- **short_script_briefs**: short script briefs

## Origin

Confidence: 92%
