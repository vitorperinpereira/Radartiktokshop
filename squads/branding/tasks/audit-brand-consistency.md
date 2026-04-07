---
task: Audit Brand Consistency
responsavel: "@brand-qa"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - all components: All React components in the component library
  - tokens_file: Output from build-design-tokens-file task
  - brand_manifesto: Output from define-brand-principles task
Saida: |
  - consistency_report: Coverage score, hardcoded value list, a11y violations, visual regression notes
Checklist:
  - "[ ] Check token usage in all components"
  - "[ ] Run contrast validation"
  - "[ ] Verify focus states"
  - "[ ] Test keyboard navigation"
  - "[ ] Check responsive behavior"
  - "[ ] List any hardcoded values"
---

# audit-brand-consistency

Produces a brand consistency audit report across all components.
