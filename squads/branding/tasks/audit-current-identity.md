---
task: Audit Current Identity
responsavel: "@brand-strategist"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - app/globals.css: Current global styles and CSS custom properties
  - components/: All existing React components
  - docs/architecture/frontend-architecture.md: Frontend architecture documentation
  - .aiox-core/docs/standards/AIOX-COLOR-PALETTE-V2.1.md: Formalized color palette standard
Saida: |
  - identity_gap_analysis: Current state vs formalized design system, what exists, what is missing, what needs tokenizing
Checklist:
  - "[ ] Map all CSS custom properties"
  - "[ ] Catalog all component classes"
  - "[ ] Identify hardcoded values"
  - "[ ] List undocumented patterns"
  - "[ ] Assess editorial metaphor adherence"
---

# audit-current-identity

Produces a gap analysis between the existing visual identity and a formalized design system.
