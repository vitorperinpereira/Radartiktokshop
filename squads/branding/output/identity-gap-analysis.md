# Identity Gap Analysis - Creator Product Radar

**Task:** audit-current-identity  
**Agent:** @brand-strategist  
**Date:** 2026-03-22  
**Status:** Complete  
**Source files:** `branding-book.md`, `frontend/tailwind.config.js`, `frontend/src/pages/LandingPage.jsx`, `frontend/src/components/layout/AppShell.jsx`, `frontend/src/pages/ProductDetail.jsx`, `apps/dashboard/app.py`, `apps/dashboard/templates/`

---

## 1. What Is Already Aligned

| Area | Current truth |
| --- | --- |
| Core product thesis | `docs/prd.md` clearly positions the product as a CLI-first weekly opportunity system |
| Visual anchor | pink, cyan, green, amber, warm white, and dark shell are already present in Vite |
| Signed-in feature model | `Radar Semanal`, `Raio-X do Produto`, `Laboratorio de Angulos`, `Minha Garagem` exist in the React app |
| Shell identity | `Estudio do Criador` is already established in `AppShell.jsx` |
| Product system name | `Creator Product Radar` is already established in package and Python surfaces |

---

## 2. Naming Drift

This remains the largest brand gap in the repo.

| Name | Where it appears | Problem |
| --- | --- | --- |
| `TikTok Scrapper` | repo and local workspace | should stay technical and internal |
| `Creator Product Radar` | package, API, Streamlit | correct formal product name, but not used everywhere |
| `Estudio do Criador` | React shell, dashboard templates | correct workspace label, but not yet shared by Python read surfaces |
| `Radar` | landing, breadcrumbs, CTA shorthand | correct short brand, but not clearly separated from the formal product name in all surfaces |

### Verdict: Naming

The names themselves are not the issue. The issue is that they were previously undocumented and therefore used as if interchangeable.

Priority: `P0`

---

## 3. Typography Split

The repo currently has two typography realities.

| Surface | Current state |
| --- | --- |
| React app | Inter everywhere, with heavy weights doing most of the brand work |
| HTML dashboard templates | some templates already experiment with Bricolage Grotesque + DM Sans |
| Streamlit core page | no strong branded type system, mostly technical utility text |

### Verdict: Typography

The future type direction exists in pieces, but the main app has not adopted it yet. This creates a split where experiments feel more branded than the primary product surface.

Priority: `P1`

---

## 4. Color Semantics Gap

The palette is recognizable, but the semantic layer is still incomplete.

| Gap | Evidence |
| --- | --- |
| destructive color collides with brand color | `danger` still aliases `primary` in `frontend/tailwind.config.js` |
| some pages still use literal hex values | `LandingPage.jsx`, `LoginPage.jsx`, template-local Tailwind config blocks |
| no shared export for Vite and Python templates | template surfaces repeat palette definitions instead of consuming one contract |

### Verdict: Color Semantics

The brand colors are good enough. The problem is governance and semantic extraction, not palette selection.

Priority: `P1`

---

## 5. Cross-Surface Parity Gap

The repo now has three visible UI families:

1. React public and signed-in surfaces
2. HTML dashboard templates
3. Streamlit read surface

### Where parity is strong

- module naming in React and templates
- dark-shell plus light-content pattern
- pink CTA ownership
- creator-first framing

### Where parity is weak

| Surface | Gap |
| --- | --- |
| Streamlit root page | still fully formal / technical in naming |
| React landing | still carries some generic CTA language |
| HTML templates | partly ahead of React in typography direction |
| technical docs vs UI | formal product name and workspace label still diverge in visible ways |

Priority: `P0`

---

## 6. Writing Gap

The repo voice is mostly strong, but not equally strong everywhere.

### Strong areas

- creator pain and timing language on landing
- operational CTA copy in the dashboard
- CLI-first framing in Streamlit

### Weak areas

| Issue | Example |
| --- | --- |
| generic public CTA | `Comecar Agora`, `Ver Demonstracao` |
| descriptive but non-guiding empty states | `Nenhuma execucao encontrada.` |
| mixed legal/footer language | `Terms`, `Privacy`, `Support` in login |

Priority: `P1`

---

## 7. Design-System Maturity Gap

There is still no shared, explicit token package in the repo.

| Current source | Limitation |
| --- | --- |
| `frontend/tailwind.config.js` | Vite-only source of truth |
| `frontend/src/index.css` | small helper layer, not a full semantic contract |
| template-local Tailwind config blocks | repeated definitions, easy to drift |

### Verdict: Design-System Maturity

The repo has a visual system, but not yet a reusable brand token architecture.

Priority: `P1`

---

## 8. Asset and Reference Gap

The most dangerous previous issue was documentation claiming non-existent surfaces.

That gap is now solved in the parent branding book, but it remains a governance warning:

- every future branding artifact must reference real files
- every target-state idea must be labeled as target-state
- every cross-surface recommendation must name the current source file

Priority: `P0`

---

## 9. Priority Summary

| Priority | Gap |
| --- | --- |
| `P0` | naming governance across repo, Vite, Streamlit, and templates |
| `P0` | keep docs tied to real files and real surfaces only |
| `P1` | split brand pink from destructive red |
| `P1` | unify typography direction across React and template surfaces |
| `P1` | extract a shared semantic token contract |
| `P1` | sharpen empty/error/CTA writing in weaker surfaces |
| `P2` | formalize Streamlit rename only after cross-surface naming decision |

---

## 10. Recommendation

The repo does not need a new brand concept. It needs disciplined alignment.

Recommended order:

1. lock naming across surfaces
2. extract semantic color tokens
3. resolve the type split between React and templates
4. tighten weaker public and empty-state copy
5. decide whether Streamlit stays formal or joins the workspace label

---

Produced by @brand-strategist for Branding & Design System Squad
