---
task: Architect Token System
responsavel: "@design-system-architect"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - brand_manifesto: Output from define-brand-principles task
  - identity_gap_analysis: Output from audit-current-identity task
Saida: |
  - token_architecture: Three-layer structure definition, naming conventions, file organization, consumption rules
Checklist:
  - "[ ] Define primitive/semantic/component layers"
  - "[ ] Establish naming convention"
  - "[ ] Define token file structure"
  - "[ ] Document override rules"
  - "[ ] Specify CSS custom property format"
---

# architect-token-system

Designs the three-layer token architecture that becomes the single source of truth.
