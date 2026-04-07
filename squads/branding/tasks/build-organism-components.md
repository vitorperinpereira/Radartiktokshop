---
task: Build Organism Components
responsavel: "@component-builder"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - molecule_components: Output from build-molecule-components task
  - tokens_file: Output from build-design-tokens-file task
  - components/command-studio.tsx: Existing command studio component
Saida: |
  - organism_components: CommandStudio, VoiceSheet, SessionFeed, HeroSection refactored to use atoms/molecules
Checklist:
  - "[ ] Refactor existing components to use atoms/molecules"
  - "[ ] Preserve existing visual identity"
  - "[ ] Validate no regression"
  - "[ ] Maintain API compatibility"
  - "[ ] Document composition"
---

# build-organism-components

Refactors existing page-level components to use the atomic component library.
