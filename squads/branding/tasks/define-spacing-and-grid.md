---
task: Define Spacing And Grid
responsavel: "@visual-designer"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - token_architecture: Output from architect-token-system task
  - app/globals.css: Current global styles and CSS custom properties
Saida: |
  - spacing_system: Spacing scale, grid definitions, layout tokens, border-radius scale, shadow system
Checklist:
  - "[ ] Define base unit and scale"
  - "[ ] Formalize grid patterns (hero, studio, ribbon)"
  - "[ ] Create border-radius scale"
  - "[ ] Tokenize shadow elevations"
  - "[ ] Document layout breakpoints"
---

# define-spacing-and-grid

Formalizes spacing, grid, elevation, and layout tokens.
