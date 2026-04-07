# Motion System - Creator Product Radar

**Task:** define-motion-tokens  
**Agent:** @motion-designer  
**Date:** 2026-03-22  
**Status:** Complete  
**Inputs:** frontend/src/index.css, frontend/src/components/layout/MobileMenu.jsx, frontend/src/components/dashboard/RankingDashboard.jsx, frontend/src/pages/SavedProducts.jsx, frontend/src/pages/ContentIdeas.jsx, apps/dashboard/templates/

---

## 1. Motion Character

The product motion should feel:

- fast
- sharp
- functional
- slightly premium

This is not a floaty or ornamental brand. Motion exists to reinforce hierarchy, focus, and action.

---

## 2. Current Implemented Patterns

### Hover lift

Defined in `frontend/src/index.css` as `.hover-lift`.

Current behavior:

- `transform 0.2s ease`
- small upward movement
- shadow increase on hover

This is the default brand hover language for premium cards.

### Gauge draw

Defined in `frontend/src/index.css` as `.gauge-circle`.

Current behavior:

- `stroke-dasharray 1s ease-out`

This gives score visuals a sense of reveal without becoming theatrical.

### Mobile menu entrance

Used in `frontend/src/components/layout/MobileMenu.jsx`.

Current behavior:

- right-side slide in
- dark overlay behind the panel
- fast duration (`duration-200`)

### Card and image emphasis

Used across landing, garage, and detail surfaces.

Examples:

- image scale on hover
- card shadow increase
- small translateY on hover
- pulse or spin states for loading and trend emphasis

---

## 3. Motion Rules

1. Keep interaction motion under the user's notice threshold for routine actions.
2. Use movement to confirm focus, not to decorate empty space.
3. Prefer quick hover and press feedback over large entrance choreography.
4. Let score visuals animate, but only as a support signal.
5. Public pages can use slightly richer reveal moments than dashboard work surfaces.

---

## 4. Recommended Timing Bands

| Band | Usage |
|------|-------|
| `~200ms` | hover, menu, card emphasis, button feedback |
| `300-500ms` | section or page reveal, only when needed |
| `~1s` | data draw or gauge motion |

These bands describe current repo behavior and should guide future cleanup.

---

## 5. Surface Guidance

### Landing

- allow a little more drama in hero cards and CTA states
- keep module cards feeling premium, not playful

### Dashboard and detail views

- prioritize scan speed
- use motion to confirm hover, open, or selection
- avoid large background or decorative animation

### Mobile navigation

- preserve direct slide-in behavior
- keep overlay and panel timing tight

---

## 6. Current Gaps

| Gap | Evidence | Priority |
|-----|----------|----------|
| no formal reduced-motion policy in the React app | current motion is ad hoc across classes and Tailwind utilities | P1 |
| no shared motion token naming | durations are implied in class usage, not documented as a contract | P1 |
| template surfaces may diverge in transition choices | HTML templates define local animation behavior | P2 |

---

## 7. Do / Do Not

### Do

- keep hover movement small
- use shadow and movement together for premium emphasis
- use loading motion only when it improves orientation
- reserve longer motion for clearly meaningful reveals

### Do Not

- do not add constant background animation to dense data surfaces
- do not stack multiple motions on the same component without a reason
- do not let mobile menu transitions become slower than dashboard interaction
- do not use motion to compensate for weak hierarchy

---

## 8. Recommendation

The next motion step should be documentation-backed cleanup, not new animation styles.

Recommended order:

1. define shared motion names and timing bands
2. add reduced-motion handling
3. normalize hover and menu behavior across React and templates

---

*Produced by @motion-designer for Branding & Design System Squad*
