# Type System - Creator Product Radar

**Task:** define-type-scale  
**Agent:** @typography-lead  
**Date:** 2026-03-22  
**Status:** Complete  
**Inputs:** branding-book.md, frontend/tailwind.config.js, frontend/src/index.css, frontend/src/pages/LandingPage.jsx, frontend/src/pages/LoginPage.jsx, apps/dashboard/templates/content_ideas.html, apps/dashboard/templates/saved_products.html

---

## 1. Current Typography Truth

The current React frontend is still effectively an Inter system.

| Layer | Current source |
|-------|----------------|
| Body font | `frontend/src/index.css` sets `Inter` on `body` |
| Display alias | `fontFamily.display` in `frontend/tailwind.config.js` also resolves to `Inter` |
| Headline style | Heavy `font-black`, tight tracking, large Tailwind sizes |
| Shell style | Bold labels, compact navigation, dense dashboard rhythm |

This means the repo already has a strong hierarchy, but not yet a distinctive family pairing.

---

## 2. Implemented Scale Patterns

The current repo uses a practical scale rather than formal type tokens.

| Tier | Typical usage | Current examples |
|------|---------------|------------------|
| Meta / micro | `text-[10px]` to `text-xs` | score labels, form dividers, module tags |
| Support | `text-sm` | helper copy, metadata, nav labels |
| Body | `text-base` to `text-lg` | dashboard paragraphs, landing support copy |
| Section heading | `text-xl` to `text-3xl` | cards, page subheads, pricing plan names |
| Page heading | `text-3xl` to `text-4xl` | `Radar Semanal`, `Minha Garagem`, `Historico do Pipeline` |
| Hero heading | `text-5xl` to `text-7xl` | landing and login headline treatment |

---

## 3. Weight Rules in Practice

| Weight style | Current role |
|--------------|--------------|
| `font-medium` | support labels, metadata, shell states |
| `font-semibold` | smaller CTA and utility emphasis |
| `font-bold` | page titles, nav items, cards |
| `font-black` | hero lines, top scores, premium CTA moments |

### Current brand takeaway

The repo already speaks in a bold voice. The problem is not weak hierarchy. The problem is that the hierarchy still relies on weight alone instead of a more distinctive family pairing.

---

## 4. Surface-Specific Rules

### Landing

The landing page should stay the loudest surface in the system.

**Reference:** `frontend/src/pages/LandingPage.jsx`

Rules:

- use black-weight headlines
- keep lines short and punchy
- let CTA typography feel decisive, not elegant

### Signed-in workspace

The workspace should compress slightly for speed.

**References:**

- `frontend/src/components/layout/AppShell.jsx`
- `frontend/src/components/dashboard/RankingDashboard.jsx`
- `frontend/src/pages/ProductDetail.jsx`

Rules:

- page titles stay bold and tight
- metadata stays lighter and quieter
- numeric score treatment should stand apart from paragraph text

### Python templates

The HTML templates under `apps/dashboard/templates/` already show a partial future direction.

Examples:

- `apps/dashboard/templates/content_ideas.html` uses Bricolage Grotesque + DM Sans
- `apps/dashboard/templates/saved_products.html` uses the same pairing

This creates an important split: some template experiments already feel closer to the target brand than the main Vite app.

---

## 5. Target Brand Direction

The branding book already defines the recommended future pairing:

| Role | Target family | Reason |
|------|---------------|--------|
| Display | Bricolage Grotesque | more creator-native character |
| Body | DM Sans | cleaner UI rhythm and readability |
| Mono | system monospace | technical labels, code, exported data |

This is target direction, not current shipped truth for the Vite app.

---

## 6. Migration Rules

1. Do not pretend the Vite app already uses the target pair.
2. Preserve the current strong hierarchy when the font upgrade lands.
3. Migrate shell, landing, and dashboard together to avoid mixed character across the same product.
4. Keep score numerals visually stronger than surrounding copy through size and weight, even before any family change.

---

## 7. Do / Do Not

### Do

- Keep headlines compact and assertive.
- Use uppercase micro labels sparingly for status and modules.
- Let numbers feel like data, not paragraph text.
- Treat dashboard text density as an operational advantage.

### Do Not

- Do not flatten the system into all-medium Inter.
- Do not introduce multiple experimental font pairs across React pages.
- Do not let landing typography become generic SaaS hero copy.
- Do not claim the target brand fonts are fully implemented across the repo.

---

## 8. Immediate Recommendations

| Recommendation | Why |
|----------------|-----|
| Lock Inter as the explicit current React truth | avoids pretending the upgrade already happened |
| Document Bricolage + DM Sans as target-only | keeps future work aligned |
| Audit page-level raw typography classes before any font migration | prevents a new family from exposing inconsistent sizing |
| Reuse one type contract across Vite and dashboard templates when extraction starts | reduces cross-surface drift |

---

*Produced by @typography-lead for Branding & Design System Squad*
