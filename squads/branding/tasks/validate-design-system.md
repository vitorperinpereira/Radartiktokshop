---
task: Validate Design System
responsavel: "@brand-qa"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - consistency_report: Output from audit-brand-consistency task
  - all outputs from previous tasks: Complete set of design system artifacts
Saida: |
  - gate_decision: PASS/CONCERNS/FAIL with detailed report
Checklist:
  - "[ ] Verify all tokens are consumed"
  - "[ ] Verify a11y compliance"
  - "[ ] Verify editorial metaphor preserved"
  - "[ ] Verify no regression from current UI"
  - "[ ] Confirm component coverage"
  - "[ ] Issue gate decision"
---

# validate-design-system

Final quality gate for the complete design system.
