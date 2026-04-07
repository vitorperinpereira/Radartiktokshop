# Token Architecture - Creator Product Radar

**Task:** architect-token-system  
**Agent:** @design-system-architect  
**Date:** 2026-03-22  
**Status:** Complete  
**Inputs:** branding-book.md, frontend/tailwind.config.js, frontend/src/index.css, apps/dashboard/templates/, color-system.md, type-system.md

---

## 1. Current State

The repo does not yet have a shared token package.

Current sources of truth are split across:

- `frontend/tailwind.config.js`
- `frontend/src/index.css`
- template-local `tailwind.config` blocks inside `apps/dashboard/templates/`

This is workable for today, but fragile for future brand rollout.

---

## 2. Recommended Architecture

The token model should follow three layers.

```text
Brand primitives
  -> semantic product tokens
  -> surface aliases
```

### Layer 1 - Brand primitives

These are raw values only.

Examples:

- pink `#FF0050`
- cyan `#00F2FE`
- green `#00E676`
- amber `#FFD54F`
- warm white `#F9F9F6`
- dark shell `#230f15`
- surface white `#FFFFFF`
- text main `#121212`
- outline `#E5E5E5`

### Layer 2 - Semantic product tokens

These map values to meaning.

Examples:

- `action-primary`
- `highlight-support`
- `opportunity-strong`
- `opportunity-review`
- `status-danger`
- `surface-canvas`
- `surface-shell`
- `surface-card`
- `text-primary`
- `text-muted`

### Layer 3 - Surface aliases

These express usage by product area, not just by color meaning.

Examples:

- `landing-hero-accent`
- `shell-nav-active`
- `ranking-top-card-border`
- `score-high`
- `score-medium`
- `score-low`
- `pipeline-status-running`

---

## 3. Current File Mapping

| Layer | Current file | Reality |
| --- | --- | --- |
| Primitive brand values | `frontend/tailwind.config.js` | main live source |
| Helper styles | `frontend/src/index.css` | light utility layer |
| Surface-local overrides | `apps/dashboard/templates/*.html` | repeated local copies |

---

## 4. Rules

1. React and template surfaces should not define competing color names for the same meaning.
2. Surface aliases should reference semantic tokens, not raw hex values.
3. Streamlit copy and page titles can keep formal naming while still consuming the same visual token set.
4. Typography direction should use the same token names even if the font rollout is staged.
5. New template experiments must not create a second design system by accident.

---

## 5. Suggested Naming Convention

Use concise kebab-case names grouped by role.

### Colors

- `brand-primary`
- `brand-accent`
- `status-success`
- `status-warning`
- `status-danger`
- `surface-canvas`
- `surface-shell`
- `surface-card`

### Typography

- `font-display`
- `font-body`
- `font-mono`
- `type-hero`
- `type-page-title`
- `type-section-title`
- `type-body`
- `type-meta`

### Motion

- `motion-hover-fast`
- `motion-enter-standard`
- `motion-gauge-draw`

### Radius and elevation

- `radius-card`
- `radius-pill`
- `shadow-soft`
- `shadow-hover`

---

## 6. Extraction Path

The repo should not jump straight into a large design-system rewrite. Use this order:

1. Keep `frontend/tailwind.config.js` as the temporary source of truth.
2. Define semantic names that both React and template surfaces can share.
3. Remove literal hex duplication from individual pages and template blocks.
4. If extraction becomes necessary later, move the shared contract into a repo-managed package or generated token file.

Important:

- extraction is a future implementation step
- it is not already complete in this repo

---

## 7. Anti-Patterns

- per-template palette forks
- page-local hardcoded pink variants
- formal docs claiming a token layer exists when only Tailwind values exist
- React and Python surfaces using different names for the same state color
- typography tokens that describe a future font stack as if it were already live

---

## 8. Decision

The right next move is semantic unification, not a brand redesign.

This repo already knows what the brand should look like. It still needs one reusable naming contract for that look.

---

Produced by @design-system-architect for Branding & Design System Squad
