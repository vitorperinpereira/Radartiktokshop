---
task: Define UX Writing Guide
responsavel: "@content-designer"
responsavel_type: agent
atomic_layer: task
Entrada: |
  - brand_manifesto: Output from define-brand-principles task
  - app/page.tsx: Main page with current UI text
  - components/command-studio.tsx: Command studio component with interface text
Saida: |
  - ux_writing_guide: Microcopy patterns, label conventions, tone rules, product glossary
Checklist:
  - "[ ] Audit current UI text"
  - "[ ] Define tone per context"
  - "[ ] Create microcopy templates (empty, error, loading, success)"
  - "[ ] Build product glossary"
  - "[ ] Document label conventions"
---

# define-ux-writing-guide

Creates the UX writing guidelines for consistent interface text.
