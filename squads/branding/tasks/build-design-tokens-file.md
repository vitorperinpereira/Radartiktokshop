---
task: Build Design Tokens File
responsavel: "@design-system-architect"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - color_system: Output from define-color-system task
  - type_system: Output from define-type-scale task
  - spacing_system: Output from define-spacing-and-grid task
  - motion_system: Output from define-motion-tokens task
Saida: |
  - tokens_file: CSS custom properties file or Tailwind config organized in three layers
Checklist:
  - "[ ] Merge all token definitions"
  - "[ ] Organize by layer (primitive/semantic/component)"
  - "[ ] Generate CSS file"
  - "[ ] Validate no naming conflicts"
  - "[ ] Ensure backwards compatibility with existing globals.css"
---

# build-design-tokens-file

Produces the unified design tokens file that replaces scattered CSS custom properties.
