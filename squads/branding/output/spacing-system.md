# Spacing & Grid System - Creator Product Radar

**Task:** define-spacing-system  
**Agent:** @layout-specialist  
**Date:** 2026-03-22  
**Status:** Complete  
**Inputs:** frontend/src/pages/LandingPage.jsx, frontend/src/components/layout/AppShell.jsx, frontend/src/components/dashboard/RankingDashboard.jsx, frontend/src/pages/ContentIdeas.jsx, frontend/src/pages/SavedProducts.jsx, apps/dashboard/templates/

---

## 1. Current Layout Rhythm

The repo already has a recognizable spacing rhythm even though it is not yet documented as one system.

| Tier | Typical classes | Usage |
|------|-----------------|-------|
| Tight | `gap-2`, `gap-3`, `p-2`, `p-3` | badges, compact nav rows, chips, score labels |
| Core | `gap-4`, `p-4`, `px-4`, `py-4` | list rows, mobile shells, small cards |
| Comfortable | `gap-6`, `p-6` | standard card padding, detail panels |
| Spacious | `gap-8`, `p-8` | major sections, landing modules, dashboard breathing room |
| Hero | `p-10`, `py-24`, `max-w-7xl` sections | landing hero and large marketing blocks |

---

## 2. Container Rules

### Public marketing surfaces

Current pattern:

- outer width: `max-w-7xl`
- large vertical sections: `py-24`
- strong two-column hero compositions

**Reference:** `frontend/src/pages/LandingPage.jsx`

### Signed-in dashboard surfaces

Current pattern:

- centered working width around `max-w-5xl`
- page padding from `p-4` mobile to `p-8` or `p-10` desktop
- cards stacked with `space-y-6` to `space-y-8`

**References:**

- `frontend/src/components/dashboard/RankingDashboard.jsx`
- `frontend/src/pages/ProductDetail.jsx`
- `frontend/src/pages/PipelineHistory.jsx`

### Focused task surfaces

Current pattern:

- narrower content width such as `max-w-[800px]`
- heavier vertical stacking
- notebook-style or editorial panel feel

**Reference:** `frontend/src/pages/ContentIdeas.jsx`

---

## 3. Shell Structure

The shell uses space as orientation.

| Element | Current pattern |
|---------|-----------------|
| Desktop sidebar | `w-64`, fixed identity area, nav stack, plan footer |
| Mobile header | compact `p-4`, brand mark + title + single action |
| Main work area | centered content with room for ranking hero and detail panels |

This is one of the strongest structural patterns in the product and should be preserved.

---

## 4. Grid Patterns

### Landing

- hero: 2-column desktop, 1-column mobile
- solution section: 12-column asymmetry for feature emphasis
- pricing: 3-column cards with the middle tier elevated

### Workspace

- ranking list: stacked feed
- product detail: 3/5 plus 2/5 desktop split
- garage: 1 to 4 column responsive card grid

### Template surfaces

The HTML templates mostly mirror these same patterns, which is good. The problem is not layout direction. The problem is repeated local definitions.

---

## 5. Radius and Density

Current radius language:

| Shape | Typical usage |
|-------|---------------|
| `rounded-lg` | dashboard cards, inputs, secondary CTAs |
| `rounded-xl` | premium cards, larger modules |
| `rounded-2xl` | hero modules, landing features, special containers |
| `rounded-full` | badges, plan pills, status dots |

### Density guidance

- Public pages can breathe more.
- Signed-in workspace should stay denser and more scannable.
- Content idea and detail surfaces can open up slightly when the user is reading, not comparing.

---

## 6. Current Gaps

| Gap | Evidence | Priority |
|-----|----------|----------|
| no explicit spacing contract | rhythm lives only in repeated Tailwind classes | P1 |
| some templates use local spacing choices outside React rhythm | template-local HTML files | P1 |
| public CTA sections and dashboard panels are consistent in feel, but not governed by one documented scale | landing and workspace follow pattern informally | P2 |

---

## 7. Spacing Rules

### Do

- keep the shell compact and the content readable
- use tighter spacing for data scan zones
- use wider spacing only where persuasion or reading is the goal
- preserve the elevated middle-plan treatment on pricing surfaces

### Do Not

- do not make dashboard cards as airy as landing sections
- do not introduce one-off giant paddings inside utility panels
- do not flatten all radii to the same size
- do not let template surfaces invent a different spacing language

---

## 8. Recommendation

Document the current spacing rhythm as a shared contract before extracting any formal token package.

The repo already behaves like it has a spacing system. It just has not named one yet.

---

*Produced by @layout-specialist for Branding & Design System Squad*
