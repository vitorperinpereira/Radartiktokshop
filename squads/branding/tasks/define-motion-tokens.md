---
task: Define Motion Tokens
responsavel: "@motion-designer"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - token_architecture: Output from architect-token-system task
  - app/globals.css (existing transitions): Current transition and animation definitions
Saida: |
  - motion_system: Easing tokens, duration scale, animation patterns, reduced-motion fallbacks
Checklist:
  - "[ ] Define easing curves"
  - "[ ] Create duration scale"
  - "[ ] Document hover/focus/enter/exit patterns"
  - "[ ] Formalize existing CSS transitions"
  - "[ ] Add prefers-reduced-motion rules"
---

# define-motion-tokens

Tokenizes all animation and transition patterns.
