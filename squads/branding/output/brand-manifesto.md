# Brand Manifesto - Creator Product Radar

**Task:** define-brand-principles  
**Agent:** @brand-strategist  
**Date:** 2026-03-22  
**Status:** Complete  
**Inputs:** branding-book.md, docs/prd.md, frontend/src/pages/LandingPage.jsx, frontend/src/components/layout/AppShell.jsx, apps/dashboard/app.py

---

## Brand Premise

**Creator Product Radar is a weekly opportunity intelligence system for TikTok Shop affiliate creators.**

It is not a generic analytics panel and not a passive trend feed. It is a working radar: a product surface that helps creators decide what to push this week, why it matters, and what action to take next.

The brand must feel:

- fast enough for creator workflow
- evidence-led instead of hype-led
- bold enough to stand out from generic SaaS dashboards
- operational enough to earn trust week after week

---

## 1. Core Principles

### P1 - Score Before Hype

Every important screen should privilege rank, score, evidence, or next action over decoration. The user should understand what matters before they admire the interface.

**Governs:** dashboard hierarchy, ranking cards, drilldown summaries, CTA placement.

### P2 - Creator-Native Urgency

The language and visual system should feel fluent in the rhythm of creators: trends move fast, saturation is real, and timing matters. This creates urgency without falling into gimmicks.

**Governs:** landing copy, module naming, badges, empty states, timing language.

### P3 - Neon on Neutral

The brand is recognizable because hot pink and cyan hit against restrained surfaces. The accents must stay loud, but the canvas must stay clean.

**Governs:** palette use, gradients, CTA emphasis, score highlights, shell contrast.

### P4 - Operational Confidence

The product should read like a working console for weekly decisions, not like a motivational landing page pasted into an app shell. Bold claims need supporting structure.

**Governs:** dashboard copy, explainability framing, pipeline history, system labels.

### P5 - Light Canvas, Dark Shell

The signed-in experience uses contrast intentionally: dark navigation, lighter working surfaces, sharp active states. This creates speed and orientation.

**Governs:** AppShell structure, navigation, dashboard cards, mobile menu continuity.

### P6 - CLI Truth, UI Clarity

The CLI remains the operational source of truth. The UI exists to reveal ranking, review, and action pathways more clearly, not to become a second control plane.

**Governs:** docs language, dashboard positioning, Streamlit narrative, observability framing.

---

## 2. Brand Personality

| Attribute | Expression | Avoid |
|-----------|------------|-------|
| Bold | Pink CTA, hard hierarchy, punchy headlines | Loud chaos or visual clutter |
| Precise | Scores, filters, rank, explainability, week labels | Vague "insights" language |
| Creator-native | TikTok Shop vocabulary, hooks, angles, creator plans | Corporate BI jargon |
| Energetic | Cyan support accents, fast motion, active badges | Slow luxury editorial posture |
| Trustworthy | Read-only dashboards, reproducible scores, explicit operator flow | Mystique or black-box copy |

---

## 3. Surface Modes

### Public Mode

Used in `frontend/src/pages/LandingPage.jsx` and `frontend/src/pages/LoginPage.jsx`.

Public mode should:

- sell momentum and aspiration
- use larger headlines and sharper promises
- keep CTAs short and direct
- frame modules as outcomes: Radar, Raio-X, Laboratorio

### Workspace Mode

Used in the Vite signed-in shell under `frontend/src/components/layout/` and page components under `frontend/src/pages/`.

Workspace mode should:

- foreground decisions and product status
- compress copy for scan speed
- keep `Estudio do Criador` as the shell label
- use `Radar` as shorthand in breadcrumbs and CTAs

### Technical Mode

Used in `apps/api/` and `apps/dashboard/`.

Technical mode should:

- stay explicit and lower-drama
- keep `Creator Product Radar` as the canonical system name until a coordinated rename happens
- describe the operator workflow without marketing inflation

---

## 4. Product Narrative

The repo already tells a coherent story when the naming drift is removed:

1. Ingest product signals.
2. Score weekly opportunities.
3. Review the ranking.
4. Drill down into product risk and upside.
5. Turn insight into a first content angle.

The brand should reinforce that chain. It is not enough to say "find trends." The product promise is stronger:

> Find the right product early, understand the evidence, and move to a testable angle before the market saturates.

---

## 5. Signature Brand Moves

### Weekly hero product

The top opportunity is treated like a featured editorial pick, but still backed by score and action.

**Reference:** `frontend/src/components/dashboard/RankingDashboard.jsx`

### Product modules as a system

`Radar Semanal`, `Raio-X do Produto`, and `Laboratorio de Angulos` behave like one creator operating stack, not unrelated features.

**Reference:** `frontend/src/pages/LandingPage.jsx`

### Dark shell with pink state

Navigation stays quiet until the active state lights up in pink.

**Reference:** `frontend/src/components/layout/AppShell.jsx`

### Score-led detail view

The product detail page balances metrics, saturation, explainability, and action CTAs.

**Reference:** `frontend/src/pages/ProductDetail.jsx`

---

## 6. Do / Do Not

### Do

- Use `Creator Product Radar` for formal product and technical references.
- Use `Estudio do Criador` for the signed-in shell.
- Use `Radar` as the short brand in compact UI contexts.
- Keep accent usage intentional so pink remains high-value.
- Write copy that helps users decide, not just admire the surface.

### Do Not

- Do not call the public product `TikTok Scrapper` in user-facing UI.
- Do not let the app read like a generic dashboard with TikTok colors.
- Do not make claims that the current system cannot support from CLI, API, or persisted data.
- Do not import another product's editorial metaphor into this repo.
- Do not describe the dashboard as the control plane of the system.

---

## 7. Governance

This manifesto is subordinate to `branding-book.md` and should be read as the principles layer for that document.

When a conflict appears:

1. Follow `branding-book.md` for naming architecture and current implementation truth.
2. Follow this manifesto for tone, visual posture, and decision criteria.
3. If a future visual upgrade is proposed, document it as target direction until it is implemented in repo files.

---

*Produced by @brand-strategist for Branding & Design System Squad*
