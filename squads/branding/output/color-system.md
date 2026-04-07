# Color System - Creator Product Radar

**Task:** define-color-system  
**Agent:** @color-specialist  
**Date:** 2026-03-22  
**Status:** Complete  
**Inputs:** branding-book.md, frontend/tailwind.config.js, frontend/src/index.css, frontend/src/pages/LandingPage.jsx, frontend/src/components/dashboard/RankingDashboard.jsx

---

## 1. Implemented Palette

The current implementation source of truth is `frontend/tailwind.config.js`.

| Token | Hex | Current role |
|-------|-----|--------------|
| `primary` | `#FF0050` | Brand CTA, active states, short-brand emphasis |
| `accent` | `#00F2FE` | Support accent, gradient partner, data energy |
| `success` | `#00E676` | Strong opportunity, healthy outcomes |
| `warning` | `#FFD54F` | Conditional opportunity, caution states |
| `danger` | `#FF0050` | Current destructive alias, still collides with brand pink |
| `background-light` | `#F9F9F6` | Main light canvas |
| `background-dark` | `#230f15` | Dark shell and dark mode base |
| `surface` | `#FFFFFF` | Primary card surface |
| `surface-dark` | `#31151d` | Dark card and dark navigation surface |
| `text-main` | `#121212` | Main readable text |
| `text-muted` | `#8A8A8E` | Secondary metadata and support copy |
| `outline` | `#E5E5E5` | Borders and dividers |

---

## 2. Brand Meaning

### Pink

Pink is the activation color. It should communicate:

- brand recognition
- primary action
- active state
- urgency with confidence

Pink is not just decoration. If everything is pink, nothing is premium.

### Cyan

Cyan is the support accent. It should communicate:

- velocity
- data energy
- secondary highlight
- gradient contrast

Cyan should rarely dominate entire surfaces.

### Green

Green is the strongest semantic signal in the system. It marks:

- high opportunity
- positive score output
- healthy momentum

### Amber

Amber signals review, caution, or moderate upside.

### Neutral Surfaces

Warm white and near-black surfaces give the accent colors room to work. This is what keeps the product from looking like a default corporate dashboard.

---

## 3. Gradient Rules

The current brand gradient is already implied by the Vite frontend and the ranking hero card.

```css
--gradient-brand: linear-gradient(90deg, #FF0050 0%, #00F2FE 100%);
--gradient-brand-soft: linear-gradient(135deg, rgba(255, 0, 80, 0.10), rgba(0, 242, 254, 0.10));
```

### Use the gradient for

- top opportunity hero frames
- premium CTA emphasis
- shell flourishes such as avatar or plan accents

### Do not use the gradient for

- paragraph text
- dense tables
- small icons
- form borders by default

---

## 4. Semantic Mapping

| Meaning | Current implementation |
|---------|------------------------|
| Primary action | `primary` |
| Secondary highlight | `accent` |
| Strong opportunity | `success` |
| Review needed | `warning` |
| Destructive / error | currently `danger`, but still aliases `primary` |
| Main canvas | `background-light` |
| Signed-in dark shell | `background-dark` / `surface-dark` |
| Cards and content panels | `surface` |

---

## 5. Score Color System

The score system is one of the most important brand semantics in the repo.

| Band | Meaning | Color |
|------|---------|-------|
| `80-100` | Strong weekly bet | `success` |
| `60-79` | Conditional review | `warning` |
| `0-59` | Weak or risky | `primary` today, future dedicated danger |

### Current examples

- `frontend/src/components/dashboard/RankingDashboard.jsx`
- `frontend/src/pages/ProductDetail.jsx`
- `frontend/src/pages/SavedProducts.jsx`

---

## 6. Surface Guidance

### Landing and login

- Let pink own the main CTA.
- Use cyan as support glow or secondary accent.
- Keep copy readable on light surfaces.

### Signed-in workspace

- The shell should lean on neutrals first.
- Pink should identify active focus and action.
- Green and amber should remain semantic, not decorative.

### Python and HTML template surfaces

- Current templates under `apps/dashboard/templates/` already reuse the same main palette.
- Keep parity with the Vite palette rather than inventing a separate Python theme.

---

## 7. Current Gaps

| Gap | Evidence | Priority |
|-----|----------|----------|
| Brand pink and destructive pink still collide | `danger` aliases `primary` in `frontend/tailwind.config.js` | P1 |
| Some UI files still use literal hex values | `frontend/src/pages/LoginPage.jsx`, `frontend/src/pages/LandingPage.jsx`, template files | P1 |
| No shared semantic token export exists yet | palette lives inside Tailwind config and template-local config blocks | P1 |
| HTML templates diverge slightly in font and surface treatment | `apps/dashboard/templates/content_ideas.html`, `saved_products.html` | P2 |

---

## 8. Color Rules

### Do

- Use pink for the main action path.
- Use cyan to energize, not to dominate.
- Keep score colors semantic.
- Protect the light canvas so colored elements keep contrast and value.

### Do Not

- Do not use pink for every badge, alert, or chip.
- Do not add new hero hues without a token decision.
- Do not use green or amber as decorative backgrounds unrelated to score or status.
- Do not let destructive UI blend into brand UI long term.

---

## 9. Recommended Next Step

The next implementation move should be semantic extraction, not a new palette.

Recommended order:

1. Split destructive red from `primary`.
2. Centralize shared semantic names for Vite and HTML template surfaces.
3. Remove repeated literal color usage from page components.

---

*Produced by @color-specialist for Branding & Design System Squad*
