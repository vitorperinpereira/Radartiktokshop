# Brand Consistency Report - Creator Product Radar

**Task:** audit-brand-consistency  
**Agent:** @brand-qa  
**Date:** 2026-03-22  
**Status:** Complete  
**Inputs:** branding-book.md, brand-manifesto.md, color-system.md, type-system.md, ux-writing-guide.md, frontend/src/, apps/dashboard/

---

## Executive Summary

The branding documentation layer is now aligned. The runtime surfaces are only partially aligned.

| Category | Status | Notes |
|----------|--------|-------|
| Naming architecture | Partial | rules are now documented, but runtime parity is not complete |
| Color system | Partial | palette is strong, semantic extraction still pending |
| Typography | Partial | React is still Inter-first while some templates already test the future pair |
| UX writing | Partial | module naming is strong, some CTA and empty-state copy is still generic |
| Cross-surface parity | Partial | React, templates, and Streamlit do not present the same level of brand maturity |

**Overall verdict:** brand direction is coherent, but implementation still behaves like a product in transition.

---

## Findings

### P0 - Naming split across surfaces

**Evidence**

- `frontend/src/components/layout/AppShell.jsx` uses `Estudio do Criador`
- `apps/dashboard/app.py` uses `Creator Product Radar`
- repo/workspace still carries `TikTok Scrapper`

**Why it matters**

The brand now has rules, but users still encounter multiple names depending on surface.

### P1 - Brand and destructive color still collide

**Evidence**

- `danger` aliases `primary` in `frontend/tailwind.config.js`

**Why it matters**

Destructive moments and brand activation still share the same emotional signal.

### P1 - Typography maturity is uneven

**Evidence**

- React app uses Inter as both body and display
- `apps/dashboard/templates/content_ideas.html` and `saved_products.html` already experiment with Bricolage Grotesque + DM Sans

**Why it matters**

The product feels like two brand phases running at once.

### P1 - Public CTA writing is less specific than workspace CTA writing

**Evidence**

- `Comecar Agora`
- `Ver Demonstracao`
- `Adicionar`

**Why it matters**

The product voice is strongest when actions are explicit. The weaker CTAs undercut an otherwise disciplined brand system.

### P1 - Some empty states still stop at description

**Evidence**

- `Nenhum produto encontrado com esses filtros.`
- `Nenhuma execucao encontrada.`

**Why it matters**

The product is meant to move people toward action. Some empty states still stop one step too early.

### P2 - Template surfaces are visually close, but technically forked

**Evidence**

- multiple template-local Tailwind config blocks repeat brand colors and type choices

**Why it matters**

The visuals stay close today, but drift risk grows with every local copy of the same token set.

---

## Strong Areas

- `Radar Semanal`, `Raio-X do Produto`, `Laboratorio de Angulos`, and `Minha Garagem` form a clear module family
- the Vite shell uses a recognizable light-canvas plus dark-shell pattern
- landing copy understands creator timing, saturation, and content pain
- product detail and ranking surfaces are meaningfully score-led
- the parent branding book now reflects real repo files and current surface truth

---

## Recommended Order

1. Resolve naming parity between Vite and Python read surfaces.
2. Split destructive red from brand pink.
3. Decide and document the one typography rollout path for React and templates.
4. Upgrade weaker CTA and empty-state copy.
5. Extract shared semantic tokens so templates stop redefining the brand locally.

---

## Final Verdict

This is not a broken brand. It is a partially implemented brand with strong fundamentals and inconsistent rollout depth.

The current priority is not invention. It is convergence.

---

*Produced by @brand-qa for Branding & Design System Squad*
