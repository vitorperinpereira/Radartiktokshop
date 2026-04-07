---
task: Build Atomic Components
responsavel: "@component-builder"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - tokens_file: Output from build-design-tokens-file task
  - token_architecture: Output from architect-token-system task
  - brand_manifesto: Output from define-brand-principles task
Saida: |
  - atom_components: Button, Input, Label, Badge, Icon, Text, Divider, Skeleton as React components
Checklist:
  - "[ ] Implement each atom consuming tokens only"
  - "[ ] Add variant/size/state props"
  - "[ ] Write inline usage docs"
  - "[ ] Validate no hardcoded values"
  - "[ ] Test keyboard accessibility"
---

# build-atomic-components

Implements the atom layer of the component library.
