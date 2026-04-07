# Estratégia de Integração de IA — Creator Product Radar MVP

**Data:** 30 de Março de 2026
**Princípio:** IA onde amplifica humanos, matemática onde é suficiente

---

## O Problema Atual

O projeto tem três "agentes" que são 100% determinísticos — nenhum usa LLM. Isso não é errado por si só. O problema é que as heurísticas hardcoded são frágeis e limitadas:

```
viral_potential_agent.py:
  _VISUAL_KEYWORDS = {"blender", "lamp", "roller", "curling", "heatless", "vacuum", "led", "pet"}
  _HOOK_KEYWORDS = {"portable", "mini", "heatless", "pet", "led", "sunset", "roller", ...}
```

Esses 8-10 keywords são a totalidade do que o sistema "entende" sobre viralidade visual. Um produto como "Escova Alisadora Cerâmica com Íons Negativos" — que é extremamente visual e demonstrável — marcaria ZERO em hook e visual porque nenhum desses keywords aparece no título.

O `creator_accessibility_agent.py` tem o mesmo problema: usa `_AUTHORITY_RISK_KEYWORDS = {"advanced", "clinical", "expert", "professional", ...}` para penalizar produtos difíceis. Mas um produto "Kit de Microagulhamento Facial" seria pontuado como acessível (nenhuma keyword de risco), quando na realidade exige autoridade médica/estética para vender com credibilidade.

---

## A Regra de Ouro: Onde Colocar IA

```
┌─────────────────────────────────────────────────────────────┐
│                    PIPELINE DO MVP                           │
│                                                             │
│  INGESTÃO ──→ SINAIS ──→ INTERPRETAÇÃO ──→ SCORING ──→ UX  │
│     │            │            │               │          │  │
│  Apify/CSV   Extração    ┌───┴───┐     Determinístico   │  │
│  Dedup       Features    │  IA   │     (factors.py)      │  │
│  Canonical               │ AQUI  │     (aggregator.py)   │  │
│                          └───┬───┘                       │  │
│                              │                       ┌───┴──┐
│                              │                       │  IA  │
│                              │                       │ AQUI │
│                              │                       └──────┘
│                                                             │
│  ✅ Determinístico          🤖 IA (LLM)                    │
│  - Ingestão/Dedup           - Interpretar sinais ambíguos   │
│  - Feature extraction       - Avaliar viralidade visual     │
│  - Score math final         - Gerar content angles          │
│  - Decay temporal           - Classificar nicho de creator  │
│  - Rankings                 - Resumir "por quê" pro usuário │
└─────────────────────────────────────────────────────────────┘
```

**Regra:** IA interpreta e gera linguagem. Matemática calcula e ranqueia. Nunca deixe o LLM decidir o score final — ele alimenta os inputs que a matemática consome.

---

## 1. SUBSTITUIR HEURÍSTICAS POR LLM — Avaliação de Viralidade

### Problema atual
`viral_potential_agent.py` usa keyword matching para 3 componentes:
- `visual_component`: max 40pts, baseado em ~8 keywords + categoria
- `hook_component`: max 35pts, baseado em ~10 keywords
- `shareability_component`: max 25pts, baseado em preço + orders

### Solução proposta
Manter `shareability_component` determinístico (preço e orders são números) mas substituir `visual_component` e `hook_component` por avaliação via LLM.

### Implementação

```python
# services/agents/runtime/viral_potential_agent.py (novo)

import json
from openai import OpenAI
from services.shared.config import get_settings

VIRAL_ASSESSMENT_PROMPT = """Você é um analista de conteúdo do TikTok Shop Brasil.

Avalie este produto para criação de conteúdo curto (15-60 segundos):

PRODUTO: {title}
CATEGORIA: {category}
SUBCATEGORIA: {subcategory}
PREÇO: R$ {price}
DESCRIÇÃO DO RAW_PAYLOAD: {description_snippet}

Responda APENAS com JSON válido:
{{
  "visual_demo_score": <0-40>,
  "visual_reasoning": "<1 frase: por que é/não é visual>",
  "hook_score": <0-35>,
  "hook_reasoning": "<1 frase: qual gancho funciona ou por que é difícil>",
  "suggested_format": "<review|antes_depois|pov|unboxing|comparacao|tutorial_rapido>",
  "confidence": <0.0-1.0>
}}

Critérios para visual_demo_score (0-40):
- 30-40: Transformação visível clara (antes/depois), efeito imediato na câmera
- 20-29: Demonstrável mas sem "wow factor" visual instantâneo
- 10-19: Precisa de explicação verbal, pouco visual
- 0-9: Impossível demonstrar em vídeo curto

Critérios para hook_score (0-35):
- 25-35: Gera curiosidade instantânea, "eu preciso disso" imediato
- 15-24: Interessante mas precisa de contexto
- 5-14: Genérico, difícil de diferenciar
- 0-4: Sem gancho óbvio para conteúdo curto
"""


async def evaluate_viral_with_llm(agent_input: AgentScoreInput) -> dict:
    """Avalia viralidade via LLM — retorna scores parciais para o pipeline determinístico."""
    settings = get_settings()
    client = OpenAI(api_key=settings.openai_api_key)

    description_snippet = ""
    raw = agent_input.signal_values  # ou extrair do raw_payload do snapshot

    response = client.chat.completions.create(
        model=settings.openai_model,  # gpt-4.1-mini
        messages=[{
            "role": "user",
            "content": VIRAL_ASSESSMENT_PROMPT.format(
                title=agent_input.product_title,
                category=agent_input.category or "desconhecida",
                subcategory=agent_input.subcategory or "desconhecida",
                price=agent_input.signal_values.get("price_current", "N/A"),
                description_snippet=description_snippet[:500],
            )
        }],
        temperature=0.2,  # Baixa temperatura para consistência
        max_tokens=300,
        response_format={"type": "json_object"},
    )

    result = json.loads(response.choices[0].message.content)

    # IMPORTANTE: O LLM sugere scores, mas o pipeline clamp/valida
    return {
        "visual_component": max(0, min(40, result["visual_demo_score"])),
        "hook_component": max(0, min(35, result["hook_score"])),
        "suggested_format": result.get("suggested_format", "review"),
        "visual_reasoning": result.get("visual_reasoning", ""),
        "hook_reasoning": result.get("hook_reasoning", ""),
        "llm_confidence": result.get("confidence", 0.5),
    }
```

### O que muda no fluxo

```
ANTES:  título → keyword matching → visual_component (max 40) + hook_component (max 35)
DEPOIS: título + categoria + preço + descrição → LLM → visual_component + hook_component
                                                          ↓
                                                 shareability_component (determinístico)
                                                          ↓
                                                 normalized_score = sum(components)
                                                          ↓
                                                 f_viral(demo, visual, hook) → scoring/factors.py
```

**O LLM alimenta inputs. A matemática em `factors.py` e `aggregator.py` continua intacta.**

### Fallback quando LLM falha

```python
async def evaluate_viral_potential_input(agent_input: AgentScoreInput) -> AgentScoreResult:
    try:
        llm_result = await evaluate_viral_with_llm(agent_input)
        visual_component = llm_result["visual_component"]
        hook_component = llm_result["hook_component"]
    except Exception:
        # Fallback para heurística atual (keywords)
        visual_component = _resolve_visual_component_seed(agent_input)  # código existente
        hook_component = _compute_hook_from_keywords(agent_input)       # código existente

    # shareability continua determinístico
    shareability_component = _compute_shareability(agent_input)

    # ... resto do scoring igual
```

**Custo:** ~$0.001 por produto com gpt-4.1-mini. Para 200 produtos/dia = ~$0.20/dia = ~$6/mês.

---

## 2. GERAR CONTENT ANGLES — A Feature Killer

### Problema atual
O modelo `ContentAngle` existe no banco com `angle_type`, `hook_text`, `supporting_rationale` mas nenhum código gera esses dados. A tabela está vazia.

### Por que isso importa
A diferença entre "dashboard de dados" e "copiloto criativo" é exatamente isso. Um creator pequeno não quer ver "score 87, classificação EXPLOSIVE". Ele quer ver: "Esse produto está explodindo. Faça um vídeo de 15s mostrando o antes e depois. Use o gancho: 'Eu não acreditei até testar'. Creators similares estão ganhando R$800/semana com ele."

### Implementação

```python
# services/agents/runtime/content_angle_generator.py (NOVO)

CONTENT_ANGLE_PROMPT = """Você é um estrategista de conteúdo para creators pequenos do TikTok Shop Brasil.

PRODUTO: {title}
CATEGORIA: {category}
PREÇO: R$ {price}
SCORE DE VIRALIDADE: {viral_score}/100
SCORE DE ACESSIBILIDADE: {accessibility_score}/100
CLASSIFICAÇÃO: {classification}
PONTOS FORTES: {strengths}

Gere 3 ângulos de conteúdo para um creator com 1K-10K seguidores.

Responda APENAS com JSON válido:
{{
  "angles": [
    {{
      "type": "<review|antes_depois|pov|unboxing|comparacao|tutorial_rapido|storytelling>",
      "hook_text": "<frase de abertura do vídeo, max 15 palavras, em português BR>",
      "script_outline": "<3 bullets descrevendo a estrutura do vídeo de 15-30s>",
      "rationale": "<1 frase: por que esse ângulo funciona para esse produto>"
    }}
  ]
}}

REGRAS:
- Hooks devem ser em português brasileiro coloquial
- Assuma que o creator NÃO tem estúdio profissional (filma no celular)
- Priorize formatos que funcionam com 0 investimento em produção
- Cada ângulo deve ser testável em 1 hora de trabalho
"""


async def generate_content_angles(
    product_id: str,
    title: str,
    category: str,
    price: Decimal,
    viral_score: int,
    accessibility_score: int,
    classification: str,
    strengths: list[str],
    run_id: str,
    week_start: date,
) -> list[ContentAngle]:
    """Gera ângulos de conteúdo via LLM e persiste como ContentAngle."""
    settings = get_settings()
    client = OpenAI(api_key=settings.openai_api_key)

    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=[{
            "role": "user",
            "content": CONTENT_ANGLE_PROMPT.format(
                title=title,
                category=category or "geral",
                price=price,
                viral_score=viral_score,
                accessibility_score=accessibility_score,
                classification=classification,
                strengths="; ".join(strengths[:3]),
            )
        }],
        temperature=0.7,  # Mais criativo aqui
        max_tokens=600,
        response_format={"type": "json_object"},
    )

    result = json.loads(response.choices[0].message.content)

    angles = []
    for angle_data in result.get("angles", [])[:3]:
        angles.append(ContentAngle(
            product_id=product_id,
            run_id=run_id,
            week_start=week_start,
            angle_type=angle_data["type"],
            hook_text=angle_data["hook_text"],
            supporting_rationale=angle_data.get("rationale", ""),
        ))

    return angles
```

### Onde inserir no pipeline

```
aggregate_scores (determinístico)
    ↓
persist_scores (gravar ProductScore)
    ↓
generate_angles (LLM — APENAS para top N produtos)  ← NOVO
    ↓
persist_angles (gravar ContentAngle)
    ↓
finalize_success
```

**Otimização de custo:** Gere angles apenas para os top 20 produtos (classificação EXPLOSIVE + HIGH). Custo: ~$0.02/dia.

---

## 3. AVALIAR ACESSIBILIDADE POR CREATOR — Substituir Keywords

### Problema atual
`creator_accessibility_agent.py` usa `_AUTHORITY_RISK_KEYWORDS` (8 palavras) para penalizar produtos que precisam de autoridade. Isso é insuficiente.

### Solução

```python
ACCESSIBILITY_PROMPT = """Avalie se um creator PEQUENO (1K-10K seguidores) do TikTok Brasil
consegue vender este produto de forma credível SEM ser especialista.

PRODUTO: {title}
CATEGORIA: {category}
PREÇO: R$ {price}

Responda APENAS com JSON:
{{
  "authority_needed": <0-25>,
  "authority_reasoning": "<que tipo de autoridade é necessária, se alguma>",
  "audience_fit": <0-40>,
  "audience_reasoning": "<para que tipo de audiência esse produto funciona>",
  "barriers": ["<barreira 1>", "<barreira 2>"]
}}

Escala authority_needed (0 = qualquer pessoa vende, 25 = precisa ser especialista):
- 0-8: Produto universalmente demonstrável (gadgets, decoração, beleza básica)
- 9-16: Precisa de algum contexto mas não expertise (suplementos comuns, tech simples)
- 17-25: Exige credibilidade profissional (equipamento médico, ferramentas técnicas)
"""
```

### O que NÃO mudar com IA

O `price_friction_component` deve continuar determinístico — preço é um número, não precisa de interpretação:

```python
def _price_component(price: Decimal | None) -> int:
    """Isso fica como está. Número → número. Sem LLM."""
    if price is None:
        return 12
    if Decimal("8") <= price <= Decimal("30"):
        return 35
    # ...
```

---

## 4. MODELO SIR PARA PREVISÃO DE SATURAÇÃO — Física + IA

### A ideia
Modelar a adoção de um produto no TikTok como um sistema epidemiológico:

```
dP/dt = β × P × (N - P) / N  −  γ × P

P = criadores promovendo ativamente
N = tamanho estimado do nicho (creators na categoria)
β = taxa de "contágio" (quão rápido novos creators adotam)
γ = taxa de "recuperação" (quão rápido creators abandonam)
```

### Onde entra IA
Os parâmetros β e γ podem ser estimados por um LLM analisando sinais qualitativos:

```python
SATURATION_PARAMS_PROMPT = """Baseado nos sinais deste produto no TikTok Shop,
estime os parâmetros de difusão:

PRODUTO: {title}
CREATORS ATIVOS HOJE: {current_creators}
CRESCIMENTO DE CREATORS (7d): {creator_growth_7d}%
CRESCIMENTO DE VIEWS (7d): {view_growth_7d}%
PREÇO: R$ {price}
DIAS DESDE DETECÇÃO: {days_detected}

Responda com JSON:
{{
  "beta": <0.01-0.50>,
  "beta_reasoning": "<por que essa taxa de adoção>",
  "gamma": <0.01-0.30>,
  "gamma_reasoning": "<por que essa taxa de abandono>",
  "estimated_peak_days": <inteiro: dias até saturação estimada>,
  "confidence": <0.0-1.0>
}}
"""
```

### Onde entra matemática pura
A simulação numérica do modelo SIR é determinística:

```python
# scoring/saturation_model.py (NOVO)

def simulate_sir(
    current_creators: int,
    niche_size: int,
    beta: float,
    gamma: float,
    days_ahead: int = 30,
) -> list[dict]:
    """Simula modelo SIR para prever curva de saturação."""
    dt = 1.0  # resolução diária
    P = float(current_creators)
    N = float(niche_size)

    trajectory = []
    for day in range(days_ahead):
        dP = (beta * P * (N - P) / N) - (gamma * P)
        P = max(0.0, min(N, P + dP * dt))
        trajectory.append({
            "day": day,
            "active_creators": round(P),
            "saturation_pct": round(P / N * 100, 1),
            "phase": _classify_phase(P, N, dP),
        })

    return trajectory


def _classify_phase(P: float, N: float, dP: float) -> str:
    saturation = P / N
    if saturation < 0.15:
        return "EMERGENTE"
    if saturation < 0.40 and dP > 0:
        return "ACELERANDO"
    if saturation < 0.70:
        return "PICO"
    return "SATURADO"
```

### O resultado para o usuário

```
┌──────────────────────────────────────────────────────┐
│  🔬 Escova Alisadora Cerâmica                        │
│  Score: 87 (EXPLOSIVE)                               │
│  Fase atual: ACELERANDO (12 creators ativos)         │
│                                                      │
│  📈 Previsão de saturação:                           │
│  ███████░░░░░░░░ 42% do nicho em 14 dias             │
│  ████████████░░░ 78% do nicho em 28 dias             │
│                                                      │
│  ⏰ Janela de oportunidade: ~10-14 dias              │
│                                                      │
│  🎬 Ângulos de conteúdo:                             │
│  1. "Eu não acreditei no resultado" (antes/depois)   │
│  2. "POV: Seu cabelo em 3 minutos" (tutorial rápido) │
│  3. "Testei o produto viral do TikTok" (review)      │
└──────────────────────────────────────────────────────┘
```

---

## 5. MAPA COMPLETO: IA vs. DETERMINÍSTICO

| Componente | Tipo | Justificativa |
|---|---|---|
| **Ingestão (Apify, CSV, JSON)** | Determinístico | Dados estruturados, parsing simples |
| **Deduplicação (canonical key, hash)** | Determinístico | Comparação exata, O(1) |
| **Feature extraction (sinais numéricos)** | Determinístico | Extração de campos do JSON |
| **Avaliação de viralidade visual** | 🤖 **LLM** | Requer interpretação semântica do produto |
| **Avaliação de hook/gancho** | 🤖 **LLM** | Requer criatividade e conhecimento cultural |
| **Avaliação de autoridade necessária** | 🤖 **LLM** | Requer julgamento contextual |
| **Shareability (preço + orders)** | Determinístico | Números puros |
| **f_trend (saturação exponencial)** | Determinístico | Função matemática pura |
| **f_revenue (raiz quadrada)** | Determinístico | Função matemática pura |
| **f_competition/opportunity** | Determinístico | Contagem + curva matemática |
| **f_viral (composto ponderado)** | Determinístico | Combina inputs (agora melhores) do LLM |
| **f_price (gaussiana)** | Determinístico | Função matemática pura |
| **Agregação + decay + bonus** | Determinístico | `aggregator.py` intacto |
| **Estimativa β/γ para modelo SIR** | 🤖 **LLM** | Parâmetros qualitativos |
| **Simulação SIR (trajetória)** | Determinístico | Equação diferencial numérica |
| **Content Angles (hooks, scripts)** | 🤖 **LLM** | Geração de linguagem criativa |
| **Resumo explicativo ("por quê")** | 🤖 **LLM** | Traduzir scores em linguagem humana |
| **Rankings e classificação** | Determinístico | Ordenação por score final |

---

## 6. CUSTO ESTIMADO MENSAL

| Uso de LLM | Chamadas/dia | Tokens/chamada | Custo/mês (gpt-4.1-mini) |
|---|---|---|---|
| Viralidade visual | 200 produtos | ~400 tokens | ~$3.60 |
| Acessibilidade creator | 200 produtos | ~350 tokens | ~$3.15 |
| Content Angles (top 20) | 20 produtos | ~600 tokens | ~$1.08 |
| Parâmetros SIR (top 50) | 50 produtos | ~300 tokens | ~$1.35 |
| Resumo explicativo (top 20) | 20 produtos | ~400 tokens | ~$0.72 |
| **TOTAL** | | | **~$10/mês** |

Com gpt-4.1-mini a ~$0.40/1M input tokens e ~$1.60/1M output tokens, o custo é trivial. Se escalar para 2000 produtos/dia, ainda fica abaixo de $100/mês.

---

## 7. ORDEM DE IMPLEMENTAÇÃO

### Sprint 1 (3-4 dias): Content Angles
- Maior impacto visual para o usuário
- Não mexe no scoring existente
- Valida se LLM funciona bem no pipeline
- Popula tabela `content_angles` que já existe

### Sprint 2 (3-4 dias): Viralidade via LLM
- Substitui keyword matching por avaliação semântica
- Mantém fallback para heurística atual
- Melhora dramaticamente `f_viral` inputs

### Sprint 3 (2-3 dias): Acessibilidade via LLM
- Substitui `_AUTHORITY_RISK_KEYWORDS` por julgamento contextual
- Mantém `price_friction_component` determinístico

### Sprint 4 (4-5 dias): Modelo SIR + Previsão
- Implementa `scoring/saturation_model.py`
- LLM estima β/γ, simulação é determinística
- Adiciona "janela de oportunidade" ao relatório

### Sprint 5 (2 dias): Resumo Explicativo
- LLM traduz scores em linguagem humana
- "Por que esse produto?" em 2 frases para o creator

---

## 8. PRINCÍPIOS ARQUITETURAIS

1. **LLM como sensor, não como cérebro.** O LLM observa e interpreta. A matemática decide e ranqueia.

2. **Sempre com fallback.** Se a API da OpenAI cair, o sistema volta para heurísticas. Nunca bloqueie o pipeline por causa de LLM.

3. **Temperatura baixa para scoring (0.1-0.2), alta para criatividade (0.6-0.8).** Viralidade precisa de consistência. Content Angles precisam de variedade.

4. **JSON mode sempre.** Use `response_format={"type": "json_object"}` para evitar parsing frágil.

5. **Cache agressivo.** O mesmo produto não muda de viralidade em 24h. Cache os resultados do LLM por produto_id + data.

6. **Não confie cegamente.** Clamp todos os valores retornados pelo LLM: `max(0, min(40, llm_result["visual_score"]))`. O LLM pode alucinar um score de 150.

7. **Log tudo.** Salve o prompt enviado e a resposta completa do LLM no `evidence` do `AgentReasoning`. Isso permite auditar e melhorar os prompts.

---

*O LangGraph pode voltar ao projeto quando vocês tiverem múltiplos LLMs conversando entre si (ex: um agente de tendência discordando de um agente de saturação e um terceiro mediando). Até lá, um loop sequencial com chamadas async é suficiente.*
