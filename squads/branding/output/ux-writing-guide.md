# UX Writing Guide - Creator Product Radar

**Task:** define-ux-writing-guide  
**Agent:** @content-designer  
**Date:** 2026-03-22  
**Status:** Complete  
**Inputs:** branding-book.md, frontend/src/pages/LandingPage.jsx, frontend/src/pages/LoginPage.jsx, frontend/src/components/dashboard/RankingDashboard.jsx, frontend/src/pages/ProductDetail.jsx, frontend/src/pages/ContentIdeas.jsx, frontend/src/pages/PipelineHistory.jsx, apps/dashboard/app.py

---

## 1. Voice Summary

The product voice should feel:

- bold in promise
- precise in operation
- creator-native in vocabulary
- trustworthy in system feedback

Public copy can push aspiration harder. Signed-in copy should sound more operational. Technical surfaces should stay explicit and lower-drama.

---

## 2. Language Rules

| Rule | Guidance |
|------|----------|
| Primary UI language | Portuguese (BR) first |
| Technical terms | English is acceptable where it improves precision |
| Product shorthand | `Radar` |
| Workspace label | `Estudio do Criador` |
| Formal product name | `Creator Product Radar` |

---

## 3. Tone by Surface

### Landing and login

Tone: ambitious, sharp, momentum-driven

Good current examples:

- "Domine o TikTok Shop com Dados, Nao Sorte."
- "Descubra tendencias antes que elas acontecam."
- "Chega de tentar adivinhar o que vai vender."

### Signed-in workspace

Tone: precise, scan-friendly, action-first

Good current examples:

- "Radar Semanal"
- "Analisar Produto"
- "Gerar Angulo de Conteudo"
- "Voltar ao Radar"

### Technical dashboard surfaces

Tone: explicit, read-only, operator-aware

Good current examples:

- "CLI-first, read-only dashboard surface for weekly ranking review."
- "Run `db-upgrade`, `ingest-mock`, and `weekly-run` from the CLI."

---

## 4. Locked Vocabulary

| Term | Use |
|------|-----|
| `Radar Semanal` | main ranking surface |
| `Raio-X do Produto` | product detail / deep analysis surface |
| `Laboratorio de Angulos` | content-angle surface |
| `Historico do Pipeline` | pipeline execution history |
| `Minha Garagem` | saved products and status tracking |
| `Criador Pro` | active paid identity |
| `Creator Opportunity Score` | canonical technical score term |
| `Score` / `Oportunidade` | acceptable UI shorthand |

---

## 5. CTA Rules

Buttons should follow this pattern:

```text
[action verb] + [clear object]
```

### Strong current examples

- `Analisar Produto`
- `Ir para o Radar`
- `Entrar na Plataforma`
- `Explorar Radar`
- `Salvar na Garagem`

### Weaker current examples

- `Comecar Agora`
- `Ver Demonstracao`
- `Adicionar`

These are not fatal, but they are less specific than the rest of the brand system.

---

## 6. Empty State Rules

Empty states should tell the user what happens next.

### Strong current examples

- `Voce ainda nao salvou nenhum produto. Volte ao Radar Semanal para explorar oportunidades e salva-las aqui.`
- `Selecione um produto no Radar para ver angulos de conteudo.`

### Weaker current examples

- `Nenhuma execucao encontrada.`
- `Nenhum produto encontrado com esses filtros.`

These are understandable, but they stop short of guiding the user.

### Preferred pattern

```text
[what is missing]. [what the user should do next].
```

Example:

`Nenhuma execucao encontrada. Rode o pipeline semanal e volte para revisar o historico.`

---

## 7. Error State Rules

Error copy should say:

1. what failed
2. what the user can do next

### Strong structure

`Erro ao carregar produto. Volte ao Radar ou tente novamente em instantes.`

### Current repo pattern

The repo often gets step one right, but step two is inconsistent:

- `Erro ao carregar ranking`
- `Erro ao carregar historico`
- `Erro ao carregar produto`

These are clear, but they should become slightly more actionable over time.

---

## 8. Loading Rules

Loading copy should describe the active process, not just say "aguarde."

### Good current examples

- `Carregando angulos de conteudo...`
- dashboard skeleton states that keep the user oriented by layout

### Preferred formula

```text
[gerundio] + [what is being processed]
```

Examples:

- `Carregando ranking semanal...`
- `Processando angulos de conteudo...`
- `Atualizando historico do pipeline...`

---

## 9. Copy Audit Snapshot

### Strengths in the current repo

- Product module names are memorable and consistent in the React app.
- Dashboard CTAs are direct and operational.
- Landing copy understands creator pain: saturation, creative block, timing.
- Streamlit copy respects the CLI-first positioning.

### Current writing gaps

| Gap | Evidence | Priority |
|-----|----------|----------|
| Generic public CTA | `Comecar Agora`, `Ver Demonstracao` in `LandingPage.jsx` | P1 |
| Some empty states stop at description | ranking and pipeline history | P1 |
| Some technical and UI naming still diverge | `Creator Product Radar` in Streamlit vs `Estudio do Criador` in app shell | P0 |
| Footer/legal links revert to generic English labels | `Terms`, `Privacy`, `Support` in `LoginPage.jsx` | P2 |

---

## 10. Do / Do Not

### Do

- Use verbs that move the user toward a decision.
- Name the product modules consistently.
- Write public copy with speed and confidence.
- Write workspace copy with operational clarity.

### Do Not

- Do not use vague SaaS filler such as `Saiba mais`.
- Do not mix multiple names for the same feature in adjacent surfaces.
- Do not let error states end without guidance when an obvious next step exists.
- Do not over-market technical surfaces that exist for review and verification.

---

*Produced by @content-designer for Branding & Design System Squad*
