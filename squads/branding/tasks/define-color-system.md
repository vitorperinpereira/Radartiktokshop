---
task: Define Color System
responsavel: "@color-specialist"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - token_architecture: Output from architect-token-system task
  - .aiox-core/docs/standards/AIOX-COLOR-PALETTE-V2.1.md: Formalized color palette standard
  - app/globals.css: Current global styles and CSS custom properties
Saida: |
  - color_system: Primitive colors, semantic aliases, functional mappings, a11y contrast matrix, dark mode spec
Checklist:
  - "[ ] Map AIOX v2.1 palette to primitives"
  - "[ ] Create semantic aliases"
  - "[ ] Build contrast matrix"
  - "[ ] Define dark mode mappings"
  - "[ ] Document forbidden combinations"
  - "[ ] Validate WCAG AA minimum"
---

# define-color-system

Formalizes the complete color system with semantic aliases and accessibility compliance.
