# TikTok Scrapper - Branding Book

> Product brand: Creator Product Radar
> Workspace label: Estudio do Criador
> Version 1.2 - March 2026
> This document is the parent brand source of truth for this repository and the aligned branding artifacts in `squads/branding/output/`.

---

## 1. Brand Architecture

The repository currently uses four different names across technical and user-facing surfaces. They are not interchangeable.

| Layer                        | Locked Name             | Where It Appears Today                            | Rule                                                                             |
| ---------------------------- | ----------------------- | ------------------------------------------------- | -------------------------------------------------------------------------------- |
| Repository / local workspace | `TikTok Scrapper`       | folder name, local operator context               | Use only in repo, local setup, and implementation conversations                  |
| Product / system name        | `Creator Product Radar` | `package.json`, `docs/prd.md`, FastAPI, Streamlit | Use in technical docs, API, CLI-adjacent material, and formal product references |
| Workspace label              | `Estudio do Criador`    | Vite app shell, some templates, landing copy      | Use inside the signed-in application shell and productized UI chrome             |
| Short UI brand               | `Radar`                 | landing, login, breadcrumbs, feature labels       | Use in compact UI contexts, CTAs, and marketing shorthand                        |

### Brand lock rules

1. Do not call the public product `TikTok Scrapper` in marketing UI.
2. Do not call the signed-in workspace `Creator Product Radar` inside the Vite app shell unless the surface is explicitly technical.
3. Use `Radar` as the short brand, never as the technical package name.
4. Keep `Creator Product Radar` as the canonical system name for docs, API, and Streamlit until those surfaces are intentionally rebranded.

---

## 2. Brand Essence

### Who we are

Creator Product Radar is a CLI-first opportunity intelligence system for TikTok Shop affiliate creators. It ingests product signals, scores weekly opportunities, and turns raw market noise into ranked action.

### Core promise

> We surface the right product before the market saturates around it.

### Audience

- Affiliate creators who need fast weekly product direction
- Small creator operators who need evidence, not vibes
- Agencies or reviewers who need a repeatable read surface over product opportunities

### Personality

| Trait          | Expression                                                   |
| -------------- | ------------------------------------------------------------ |
| Bold           | Hot pink, sharp hierarchy, decisive CTAs                     |
| Precise        | Scores, rankings, filters, breakdowns, evidence              |
| Creator-native | TikTok Shop vocabulary, scroll-friendly pacing, strong hooks |
| Energetic      | Pink-to-cyan contrast, fast transitions, bright highlights   |
| Trustworthy    | Explainable scoring, consistent thresholds, explicit history |

### Tagline

`Radar ligado. Produto certo.`

---

## 3. Brand Positioning

The product is not a generic dashboard and not a passive analytics tool. It should feel like an operator's growth console for weekly creator decisions.

### What the brand is

- A weekly product radar for TikTok Shop opportunities
- A creator operating surface with score-driven decisions
- A bridge between research, ranking, and first content action

### What the brand is not

- A social network
- A playful creator toy
- A dark luxury editorial product
- A generic BI dashboard with corporate blue defaults

---

## 4. Visual Principles

1. Data is the hero. Every screen should earn its space by clarifying rank, risk, or action.
2. Scan beats reading. The hierarchy must survive a two-second glance.
3. Neon on neutral. Pink and cyan should hit hard because the canvas stays light and controlled.
4. Score color is semantic. Green means go, amber means caution, pink means risk or brand action.
5. The workspace is fast, not ornamental. Motion should support comprehension, never become the story.

### Visual DNA

| Element         | Signature                                                                      |
| --------------- | ------------------------------------------------------------------------------ |
| Public hero     | Warm-white canvas, pink CTAs, cyan support accents, oversized headlines        |
| App shell       | Light content area with a dark sidebar and pink active states                  |
| Top opportunity | Gradient-framed hero card with oversized score and image                       |
| Product feed    | Dense rows with rank, score, category, and immediate actions                   |
| Status language | Green for momentum or success, amber for caution, pink for risk and activation |

---

## 5. Color System

This section uses the current Vite frontend implementation in `frontend/tailwind.config.js` as the implementation source of truth.

### 5.1 Implemented core palette

| Token              | Hex       | Current role                              |
| ------------------ | --------- | ----------------------------------------- |
| `primary`          | `#FF0050` | Brand CTA, active states, hot accent      |
| `accent`           | `#00F2FE` | Complementary accent, gradient partner    |
| `success`          | `#00E676` | Positive score and healthy outcomes       |
| `warning`          | `#FFD54F` | Medium-confidence or caution states       |
| `danger`           | `#FF0050` | Current error/risk alias in Vite frontend |
| `background-light` | `#F9F9F6` | Main app canvas                           |
| `background-dark`  | `#230f15` | Signed-in dark shell / dark mode base     |
| `surface`          | `#FFFFFF` | Primary cards and white surfaces          |
| `surface-dark`     | `#31151d` | Dark cards, dark nav, dark mode surfaces  |
| `text-main`        | `#121212` | Primary readable text                     |
| `text-muted`       | `#8A8A8E` | Secondary metadata and support copy       |
| `outline`          | `#E5E5E5` | Borders and dividers                      |

### 5.2 Brand gradients

```css
--gradient-brand: linear-gradient(90deg, #ff0050 0%, #00f2fe 100%);
--gradient-brand-soft: linear-gradient(
  135deg,
  rgba(255, 0, 80, 0.1),
  rgba(0, 242, 254, 0.1)
);
```

### 5.3 Locked semantic rules

| Meaning                 | Color                                                           |
| ----------------------- | --------------------------------------------------------------- |
| Primary action          | Pink `#FF0050`                                                  |
| Highlight / data energy | Cyan `#00F2FE`                                                  |
| Strong opportunity      | Green `#00E676`                                                 |
| Conditional opportunity | Amber `#FFD54F`                                                 |
| Error / destructive     | Pink today, but should split from brand pink in a later rollout |

### 5.4 Score mapping

| Score band | Meaning            | Color                               |
| ---------- | ------------------ | ----------------------------------- |
| `80-100`   | Strong weekly bet  | `success`                           |
| `60-79`    | Conditional review | `warning`                           |
| `0-59`     | Weak or risky      | `primary` / future dedicated danger |

### 5.5 Color do / do not

- Use pink for activation and brand energy.
- Use cyan as a support accent, never as the dominant fill color for entire pages.
- Keep white/light surfaces clean so the accent colors stay expensive.
- Do not invent a fourth hero hue without a token decision.
- Do not use the pink-cyan gradient on body copy, inputs, or tiny icons.

---

## 6. Typography

The repo currently implements a simplified typography layer. The branding book should document both the current state and the intended brand direction.

### 6.1 Current implementation state

| Layer                  | Current truth                                                                |
| ---------------------- | ---------------------------------------------------------------------------- |
| Frontend body          | Inter via `frontend/src/index.css`                                           |
| Frontend display label | `fontFamily.display` also resolves to Inter in `frontend/tailwind.config.js` |
| Weight style           | Heavy `font-black` headlines, bold UI labels, dense compact rhythm           |

### 6.2 Target brand direction

| Role    | Target family       | Why                                       |
| ------- | ------------------- | ----------------------------------------- |
| Display | Bricolage Grotesque | More personality and creator-native punch |
| Body    | DM Sans             | Cleaner UI readability with modern rhythm |
| Mono    | System monospace    | Scores, CLI output, technical metadata    |

### 6.3 Rules

1. Until the font upgrade ships, use current Inter-based implementation consistently.
2. If the font upgrade lands later, it must preserve the current bold, compact hierarchy rather than flatten it.
3. Scores and numeric KPIs should visually separate from paragraph text through weight or mono treatment.
4. Marketing pages can be larger and louder; signed-in app pages stay denser and more operational.

---

## 7. Voice and Naming System

### 7.1 Tone by surface

| Surface         | Tone                                             |
| --------------- | ------------------------------------------------ |
| Landing / login | Aspirational, creator-ambitious, benefit-forward |
| Signed-in app   | Operational, precise, score-driven               |
| Streamlit / API | Technical, explicit, lower-drama                 |
| CLI / docs      | Functional and reproducible                      |

### 7.2 Locked product vocabulary

| Term                        | Use                                                 |
| --------------------------- | --------------------------------------------------- |
| `Radar Semanal`             | Main weekly ranking surface                         |
| `Raio-X do Produto`         | Deep product analysis surface                       |
| `Laboratorio de Angulos`    | Content-angle surface                               |
| `Historico do Pipeline`     | Pipeline run history                                |
| `Minha Garagem`             | Saved/bookmarked products                           |
| `Criador Pro`               | Premium or active-plan identity                     |
| `Creator Opportunity Score` | Canonical technical score label in docs and backend |
| `Score` / `Oportunidade`    | Acceptable UI shorthand                             |

### 7.3 Writing rules

1. Public UI speaks Portuguese (BR) first.
2. Technical docs and API can keep English when precision matters.
3. Buttons should be action-first: `Analisar Produto`, `Ir para o Radar`, `Entrar na Plataforma`.
4. Empty states should tell the user what to do next.
5. Avoid vague corporate verbs like `Descobrir mais`, `Continuar`, or `Saiba mais` on operational surfaces.

---

## 8. Surface Mapping

### 8.1 Public Vite surfaces

| Surface      | File                                 | Brand role                              |
| ------------ | ------------------------------------ | --------------------------------------- |
| Landing page | `frontend/src/pages/LandingPage.jsx` | Acquisition, positioning, offer framing |
| Login page   | `frontend/src/pages/LoginPage.jsx`   | Trust, conversion, premium access cue   |

### 8.2 Signed-in Vite surfaces

| Surface          | File                                                     | Brand role                                     |
| ---------------- | -------------------------------------------------------- | ---------------------------------------------- |
| App shell        | `frontend/src/components/layout/AppShell.jsx`            | Product chrome, navigation, workspace identity |
| Mobile menu      | `frontend/src/components/layout/MobileMenu.jsx`          | Mobile navigation continuity                   |
| Weekly radar     | `frontend/src/components/dashboard/RankingDashboard.jsx` | Primary weekly decision surface                |
| Product detail   | `frontend/src/pages/ProductDetail.jsx`                   | Evidence and drilldown                         |
| Content ideas    | `frontend/src/pages/ContentIdeas.jsx`                    | Action translation from insight to angle       |
| Pipeline history | `frontend/src/pages/PipelineHistory.jsx`                 | Operational trust and traceability             |
| Saved products   | `frontend/src/pages/SavedProducts.jsx`                   | User memory and follow-up                      |

### 8.3 Python surfaces

| Surface              | File                                     | Current naming             |
| -------------------- | ---------------------------------------- | -------------------------- |
| FastAPI              | `apps/api/main.py`                       | `Creator Product Radar`    |
| Streamlit entrypoint | `apps/dashboard/app.py`                  | `Creator Product Radar`    |
| Weekly radar page    | `apps/dashboard/pages/1_weekly_radar.py` | `Weekly Opportunity Radar` |

### 8.4 Cross-surface rule

The Vite app may use `Estudio do Criador` and `Radar`. The Python read surfaces may stay on `Creator Product Radar` until a coordinated rename is planned. Do not blend the labels randomly inside the same surface.

---

## 9. Signature Component Patterns

These patterns are already visible in the current Vite frontend and should be preserved.

### 9.1 Top opportunity hero card

Reference: `frontend/src/components/dashboard/RankingDashboard.jsx`

Brand cues:

- Gradient border using pink-to-cyan
- Large image-led opportunity framing
- Oversized score treatment
- Strong CTA anchored to product analysis

### 9.2 Product feed row

Reference: `frontend/src/components/dashboard/ProductRow.jsx`

Brand cues:

- Dense scan-friendly layout
- Rank + title + score visible without expansion
- Quick actions in-row
- Utility first, but still premium

### 9.3 App shell sidebar

Reference: `frontend/src/components/layout/AppShell.jsx`

Brand cues:

- Dark sidebar against lighter main content
- `movie_edit` icon as current workspace mark
- Pink active states, muted inactive nav
- Plan identity in the footer block

### 9.4 Content idea card

Reference: `frontend/src/pages/ContentIdeas.jsx`

Brand cues:

- Editorial blockquote feel for the hook
- Copy-forward hierarchy
- Small premium flourish with the top ribbon accent

### 9.5 Public growth hero

Reference: `frontend/src/pages/LandingPage.jsx`

Brand cues:

- Overstated headline
- Pink CTA dominance
- Productized modules (`Radar`, `Raio-X`, `Laboratorio`)
- Offer framing through pricing and creator ambition

---

## 10. Motion and Interaction

### Current implementation cues

| Pattern                | Current examples                        |
| ---------------------- | --------------------------------------- |
| Fast color transitions | buttons, links, nav items               |
| Small hover lift       | hero card and interactive cards         |
| Drawer motion          | mobile menu slide-in                    |
| Gauge animation feel   | radial score visuals in dashboard cards |

### Motion rules

1. Keep motion short and purposeful.
2. Hover should feel sharp, not floaty.
3. Use motion to confirm rank, focus, or transition between decision states.
4. Avoid decorative background motion on dense data surfaces.
5. Respect reduced-motion preferences whenever animation is formalized.

---

## 11. Accessibility

### Non-negotiables

- Scores must remain numeric, never color-only.
- CTA contrast must stay AA-compliant on pink.
- Icon-only controls need readable intent in context.
- Sidebar and mobile menu need visible focus handling.
- Form labels must remain explicit on login and future settings surfaces.

### Current a11y priorities

1. Preserve readable contrast on warm-white surfaces.
2. Keep empty and error states explicit, not just decorative.
3. When the design system is extracted, formalize focus rings and reduced-motion rules.

---

## 12. Current Repo Alignment

This section is the main continuation work for version 1.1.

### 12.1 What is already aligned

| Area                    | Repo truth                                                                                                  |
| ----------------------- | ----------------------------------------------------------------------------------------------------------- |
| Core palette            | Pink, cyan, green, amber, warm white, near-black are already implemented in `frontend/tailwind.config.js`   |
| Surface model           | Public landing/login plus signed-in shell plus Python read surfaces already exist                           |
| Primary brand shorthand | `Radar` is already established in public and signed-in UI                                                   |
| Feature naming          | `Radar Semanal`, `Raio-X do Produto`, `Laboratorio de Angulos`, `Minha Garagem` are already in the frontend |

### 12.2 Current gaps

| Gap                                                      | Evidence                                                                                            | Priority |
| -------------------------------------------------------- | --------------------------------------------------------------------------------------------------- | -------- |
| Naming drift across surfaces                             | `TikTok Scrapper`, `Creator Product Radar`, `Estudio do Criador`, and `Radar` coexist without rules | P0       |
| Typography not yet brand-distinctive                     | current frontend still resolves to Inter everywhere                                                 | P1       |
| Color semantics are not fully separated                  | `danger` currently aliases the same pink as `primary`                                               | P1       |
| No standalone token contract                             | palette lives in Tailwind config and component literals, not in a shared brand token package        | P1       |
| Python surfaces not yet aligned to Vite workspace naming | Streamlit and API still present `Creator Product Radar`                                             | P2       |
| Asset inventory was inaccurate                           | old branding book pointed to non-existent `apps/frontend` implementation paths                      | P0       |

### 12.3 Decision

The brand book must describe both:

- the current implemented truth
- the intended visual evolution

It must not claim target-state typography, token architecture, or assets are already live when they are not.

---

## 13. Asset Inventory

This replaces the earlier broken checklist.

| Asset                             | Status                   | Real location                                                     |
| --------------------------------- | ------------------------ | ----------------------------------------------------------------- |
| Core color tokens                 | Implemented              | `frontend/tailwind.config.js`                                     |
| Base CSS helpers                  | Implemented              | `frontend/src/index.css`                                          |
| Public landing surface            | Implemented              | `frontend/src/pages/LandingPage.jsx`                              |
| Public login surface              | Implemented              | `frontend/src/pages/LoginPage.jsx`                                |
| Signed-in shell                   | Implemented              | `frontend/src/components/layout/AppShell.jsx`                     |
| Mobile drawer navigation          | Implemented              | `frontend/src/components/layout/MobileMenu.jsx`                   |
| Weekly radar hero/list pattern    | Implemented              | `frontend/src/components/dashboard/RankingDashboard.jsx`          |
| Product detail surface            | Implemented              | `frontend/src/pages/ProductDetail.jsx`                            |
| Content-angle surface             | Implemented              | `frontend/src/pages/ContentIdeas.jsx`                             |
| Pipeline history surface          | Implemented              | `frontend/src/pages/PipelineHistory.jsx`                          |
| Saved-products surface            | Implemented              | `frontend/src/pages/SavedProducts.jsx`                            |
| Standalone brand token file       | Pending                  | not yet extracted from current frontend                           |
| Distinct typography layer         | Pending                  | current frontend still uses Inter as body and display             |
| Dedicated logo system             | Pending                  | current shell uses icon + text rather than a formal mark          |
| Shared cross-surface naming guide | Implemented by this book | `squads/branding/output/branding-book.md`                         |
| Streamlit naming parity pass      | Pending                  | `apps/dashboard/app.py`, `apps/dashboard/pages/1_weekly_radar.py` |

---

## 14. Rollout Priorities

### Phase 1 - Naming lock

- Apply the naming rules in this book to all future UI changes.
- Stop introducing new surface labels for the same concepts.
- Decide whether Python surfaces stay `Creator Product Radar` or migrate toward `Estudio do Criador`.

### Phase 2 - Token extraction

- Move Vite color and spacing decisions into a dedicated token layer.
- Separate `danger` from `primary` so destructive and brand actions stop sharing the same emotional signal.
- Remove repeated literal color usage from app components.

### Phase 3 - Typography upgrade

- Introduce the brand display/body pair intentionally.
- Preserve the current bold hierarchy and creator-native energy.
- Re-test density on dashboard-heavy views before rolling out globally.

### Phase 4 - Cross-surface parity

- Align Streamlit titles and copy with the Vite workspace naming.
- Reconcile API, docs, and UI score labels.
- Document one shared iconography and empty-state language system.

---

## 15. Do / Do Not

### Do

- Use `Radar` as the compact UI brand.
- Keep the hot pink / cyan pairing as the recognizability anchor.
- Let rank, score, and action dominate the hierarchy.
- Preserve the dark-shell plus light-canvas contrast in the signed-in experience.
- Write public copy with confidence and signed-in copy with precision.

### Do not

- Do not rename the same concept differently in each surface.
- Do not present stale implementation paths as if they already exist.
- Do not flatten the visual system into generic SaaS blue-gray patterns.
- Do not use color alone to communicate opportunity quality.
- Do not import another product's brand language into this repo's brand artifacts.

---

_TikTok Scrapper Branding Book v1.2_
_Aligned to the current Creator Product Radar / Estudio do Criador repo surfaces on 2026-03-22._
