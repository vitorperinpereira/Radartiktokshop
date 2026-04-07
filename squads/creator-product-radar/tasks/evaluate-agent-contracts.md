---
task: "Evaluate Agent Contracts"
responsavel: "@signal-scoring-architect"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - agent_outputs
  - json_schema_rules
  - confidence_expectations
Saida: |
  - contract_gaps
  - schema_updates
  - evaluation_notes
Checklist:
  - "[ ] Validate structured JSON output for each runtime agent"
  - "[ ] Check confidence ranges and fallback behavior"
  - "[ ] Reject vague explanations or missing evidence"
  - "[ ] Align contracts with API persistence needs"
---

# *evaluate-agent-contracts

Task generated from squad design blueprint for creator-product-radar.

## Usage

```
@signal-scoring-architect
*evaluate-agent-contracts
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agent_outputs` | string | Yes | agent outputs |
| `json_schema_rules` | string | Yes | json schema rules |
| `confidence_expectations` | string | Yes | confidence expectations |

## Output

- **contract_gaps**: contract gaps
- **schema_updates**: schema updates
- **evaluation_notes**: evaluation notes

## Origin

Confidence: 90%
