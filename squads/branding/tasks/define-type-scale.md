---
task: Define Type Scale
responsavel: "@typography-lead"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - token_architecture: Output from architect-token-system task
  - app/layout.tsx: Root layout with font declarations
  - app/globals.css: Current global styles and CSS custom properties
Saida: |
  - type_system: Font scale, hierarchy rules, weight mappings, line heights, responsive breakpoints
Checklist:
  - "[ ] Define size scale (12 to 68px range)"
  - "[ ] Map font families to contexts"
  - "[ ] Define weight rules per family"
  - "[ ] Set line-height ratios"
  - "[ ] Create responsive adjustments"
  - "[ ] Validate with Cormorant display sizes"
---

# define-type-scale

Formalizes the type scale and hierarchy rules for the three-font system.
