---
task: Build Molecule Components
responsavel: "@component-builder"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - atom_components: Output from build-atomic-components task
  - tokens_file: Output from build-design-tokens-file task
Saida: |
  - molecule_components: FormField, Card, ProfileCard, MetricStrip, NavItem, Tag
Checklist:
  - "[ ] Compose from atoms only"
  - "[ ] Implement consistent prop API"
  - "[ ] Add responsive behavior"
  - "[ ] Document composition patterns"
  - "[ ] Validate accessibility"
---

# build-molecule-components

Implements the molecule layer by composing atoms.
