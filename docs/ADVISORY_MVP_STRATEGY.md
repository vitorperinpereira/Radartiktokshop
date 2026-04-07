# Análise Estratégica: Creator Product Radar — MVP Advisory

**Data:** 30 de Março de 2026
**Para:** Isa — Fundadora
**De:** Consultor de Produto & Arquitetura
**Contexto:** Análise cruzada do projeto atual vs. case Kalodata + dinâmicas do TikTok Shop

---

## 1. DIAGNÓSTICO DO ESTADO ATUAL

O projeto Creator Product Radar é um monolito modular em Python com três superfícies (CLI, FastAPI, Streamlit), um pipeline semanal orquestrado via LangGraph, e um motor de scoring determinístico com 4 fatores matemáticos. A arquitetura está bem estratificada, mas há uma desconexão significativa entre a ambição do framework AIOX (com 10+ agentes, stories, epics, workflows) e a necessidade real de um MVP enxuto para validação de mercado.

### O que está sólido

O motor de scoring em `scoring/factors.py` é a joia do projeto. As quatro funções — saturação exponencial para tendência, raiz quadrada para receita, logística invertida para competição, e composto linear ponderado para viralidade — são matematicamente elegantes e refletem bem a realidade do TikTok Shop. O pipeline de ingestão com deduplicação por chave canônica e resolução de identidade de produto também é robusto.

### O que preocupa

O projeto está sofrendo de "over-engineering prematuro". Existe um React frontend, um site de marketing, um Streamlit dashboard, uma API FastAPI, um sistema de agentes AIOX com 10 personas, workflows formais de 4 fases, e um framework de governança com Constitution formal — tudo isso para um produto que ainda não tem um único usuário pagante. A Kalodata levantou capital de VC e levou anos para chegar à sua complexidade. Vocês precisam validar a hipótese central primeiro.

---

## 2. O QUE O ARTIGO DA KALODATA ENSINA PARA O SEU MVP

### 2.1 O Método de 5 Etapas é o seu produto

O artigo revela que operadores de elite do TikTok Shop cristalizaram um método empírico de 5 etapas para validação de produtos. Este método deveria ser a espinha dorsal do seu scoring, não apenas uma inspiração. Comparando com o que vocês têm:

| Etapa Kalodata | Seu Projeto Atual | Gap |
|---|---|---|
| **Filtro de Momentum** (200-500% crescimento semanal) | `f_trend` com saturação exponencial | ✅ Coberto, mas falta a faixa "sweet spot" 200-500% como classificação explícita |
| **Índice de Diversidade de Promotores** (5-15 criadores independentes) | `f_competition` conta criadores ativos | ⚠️ Invertido — vocês penalizam muitos criadores, mas não validam se há diversidade mínima |
| **Auditoria de Elasticidade de Preço** ($15-45 USD) | Não existe | ❌ Crítico — falta filtro de faixa de preço por impulso |
| **Verificação de Cadeia de Suprimentos** (Seller Type) | Não existe | ❌ Falta classificação de confiabilidade do seller |
| **Teste de Fragmentação Tática** (microlotes) | Não existe | ⚠️ Isso é comportamento do usuário, não do sistema — mas você pode guiá-lo |

### 2.2 A lição do "Contexto, não Contabilidade"

A maior lição do artigo é que GMV estimado ≠ lucro real. A Kalodata tem precisão de apenas ~50% nas estimativas de receita, e mesmo assim é a ferramenta líder. O seu projeto já adota a filosofia correta — estimação via delta de inventário e sinais públicos — mas precisa ser honesto com o usuário sobre as limitações. Não venda números absolutos; venda sinais direcionais e rankings comparativos. Isso é libertador para o MVP: você não precisa de precisão contábil, precisa de ordenação confiável.

### 2.3 Micro-influenciadores são o público-alvo E o diferencial

O artigo demonstra que nano/micro-influenciadores (1K-50K seguidores) geram o maior ROI no TikTok Shop. Seu projeto tem o modelo `Creator` no banco de dados mas nunca o popula. Isso é um erro estratégico. O diferencial do seu produto em relação à Kalodata (que custa $38-99/mês) é focar exclusivamente nesse segmento com recomendações acionáveis: "Este produto tem alta viralidade, baixa competição, e funciona para creators com menos de 10K seguidores que fazem conteúdo de beleza."

### 2.4 Frequência de atualização: semanal é lento demais

A Kalodata atualiza a cada 15 minutos. A FastMoss atualiza diariamente. Seu pipeline roda semanalmente. Para o MVP, diário já seria um salto enorme. Semanal significa que seus usuários verão tendências que já saturaram.

---

## 3. FUNCIONALIDADES A REMOVER DO MVP

Estas são as coisas que estão consumindo complexidade sem entregar valor para validação de mercado:

### 3.1 Framework AIOX inteiro

**Severidade: CRÍTICA — remover imediatamente do escopo mental**

O sistema de 10 agentes (@dev, @qa, @architect, @pm, @po, @sm, @analyst, @data-engineer, @ux-design-expert, @devops), Constitution formal, workflows de 4 fases, story-driven development, handoff protocols — tudo isso é infraestrutura de processo para uma equipe que não existe. Vocês são um time pequeno construindo via Claude Code no terminal. O AIOX está adicionando overhead cognitivo massivo sem retorno. Mantenham o CLAUDE.md com os comandos úteis e descartem o resto.

### 3.2 React Frontend (`apps/frontend/`) e Website (`apps/website/`)

**Severidade: ALTA**

Dois projetos Node.js separados com node_modules que não entregam nada para o MVP. O Streamlit dashboard ou um frontend mínimo via API é suficiente para validar. Não construam frontend custom antes de ter 50 usuários ativos.

### 3.3 LangGraph como orquestrador

**Severidade: MÉDIA**

O LangGraph está sendo usado para orquestrar um pipeline que é 100% determinístico. Os três "agentes" (trend, viral, creator_accessibility) são heurísticas puras — nenhum faz chamada a LLM. Um simples script Python sequencial faria o mesmo trabalho com 1/10 da complexidade. Guardem LangGraph para quando realmente precisarem de agentes com LLM interpretando sinais ambíguos.

### 3.4 Múltiplas superfícies simultâneas

**Severidade: MÉDIA**

CLI + FastAPI + Streamlit + React + Website = 5 superfícies para manter. Para o MVP, escolham UMA: a API FastAPI com um frontend mínimo (pode ser o próprio Streamlit). O CLI é útil para desenvolvimento, mantenham-no. Mas não mantenham 5 interfaces.

### 3.5 Backend separado (`backend/ranking_api/`)

**Severidade: BAIXA**

Serviço duplicado que replica funcionalidade já presente na FastAPI principal. Consolidem.

---

## 4. MELHORIAS PRIORITÁRIAS PARA O MVP

### 4.1 Adicionar fator de Elasticidade de Preço (f_price)

**Impacto: ALTO — implementação: ~2h**

O artigo é claro: produtos entre $15-45 USD são otimizados para compra por impulso no TikTok. Criem um quinto fator:

```python
def f_price(price: float, params: ScoringParams) -> float:
    """Score price accessibility for impulse purchase optimization.

    Sweet spot: $15-45 USD (peak at ~$25).
    Gaussian bell curve centered on optimal impulse price.
    """
    optimal = params.price_optimal  # default 25.0
    sigma = params.price_sigma      # default 12.0
    return clamp_score(100.0 * exp(-0.5 * ((price - optimal) / sigma) ** 2))
```

Isso é uma gaussiana centrada em $25 com desvio de $12 — produtos de $13-37 ficam acima de 70 pontos, caindo suavemente nas extremidades.

### 4.2 Transformar f_competition em Índice de Diversidade

**Impacto: ALTO — implementação: ~3h**

Atualmente `f_competition` é uma logística invertida simples: menos criadores = melhor. Mas o artigo ensina que o ideal é ter 5-15 criadores promovendo o produto (validação de replicabilidade). Zero criadores significa produto não testado; 1 criador significa dependência. Reformulem:

```python
def f_opportunity(n_creators: float, params: ScoringParams) -> float:
    """Score creator opportunity window.

    Peak at n_creators = sweet_spot (default 10).
    Too few = unvalidated. Too many = saturated.
    Asymmetric: saturation penalty is steeper than validation penalty.
    """
    sweet = params.creator_sweet_spot  # default 10
    if n_creators <= sweet:
        # Ramp up: product gains validation as creators join
        return clamp_score(100.0 * (n_creators / sweet) ** 0.6)
    else:
        # Decay: saturation kicks in faster
        return clamp_score(100.0 / (1.0 + exp(params.alpha * (n_creators - params.n0))))
```

### 4.3 Adicionar Estimativa de GMV via Delta de Inventário

**Impacto: ALTO — implementação: ~4h**

O artigo detalha exatamente como a Kalodata estima GMV: captura estoque em T1, captura em T2, subtrai, multiplica pelo preço. Vocês já têm `ProductSnapshot` com `raw_payload`. Implementem:

```python
def estimate_gmv(snapshot_t1, snapshot_t2) -> Decimal:
    stock_delta = max(0, snapshot_t1.stock_count - snapshot_t2.stock_count)
    return stock_delta * snapshot_t2.price
```

Com o caveat explícito no relatório: "Estimativa direcional — reposições de estoque, carrinhos abandonados e remoções manuais podem distorcer este número."

### 4.4 Implementar Classificação de Saturação Temporal

**Impacto: ALTO — implementação: ~3h**

O artigo enfatiza que quando uma tendência é "visualmente óbvia no feed", a oportunidade de arbitragem já se dissipou. Criem um classificador de fase do ciclo de vida:

```
EMERGENTE  → crescimento 200-500%, < 10 criadores, < 14 dias
ACELERANDO → crescimento > 500%, 10-30 criadores
PICO       → crescimento desacelerando, 30-80 criadores
SATURADO   → crescimento negativo ou > 80 criadores
```

Isso é muito mais acionável do que apenas um score numérico.

### 4.5 Popular o modelo Creator com dados reais

**Impacto: MÉDIO-ALTO — implementação: ~4h**

O modelo `Creator` existe no banco mas está vazio. Os dados da Apify (via `clockworks/tiktok-scraper`) já trazem informações de criadores nos vídeos. Extraiam: handle, contagem de seguidores, nicho, e cruzem com os produtos que promovem. Isso permite a funcionalidade killer: "Criadores similares a você que estão tendo sucesso com este produto."

### 4.6 Aumentar frequência para diária

**Impacto: MÉDIO — implementação: ~2h**

Renomeiem `weekly_run` para `pipeline_run` e parametrizem a frequência. Para o MVP, rodar diariamente (via cron ou scheduled task) já captura tendências 7x mais rápido. O artigo mostra que tendências no TikTok morrem em semanas — semanal é lento demais.

### 4.7 Adicionar Commission Rate como sinal de primeira classe

**Impacto: MÉDIO — implementação: ~1h**

Vocês já coletam `commission_rate` na ingestão e até validam que é > 0. Mas não usam no scoring. Para creators pequenos, a taxa de comissão é literalmente o fator mais importante — é o que determina quanto eles ganham. Integrem no `f_revenue` ou criem um fator dedicado.

---

## 5. OPORTUNIDADES ESTRATÉGICAS

### 5.1 Posicionamento: "Kalodata para creators de R$0"

A Kalodata cobra $38-99/mês e foca em sellers/agências. Vocês podem ser o "anti-Kalodata" — gratuito ou freemium ($9.90/mês), focado 100% em creators brasileiros pequenos, com recomendações em português e métricas traduzidas para a realidade BR. O TikTok Shop está expandindo no Brasil e não há ferramenta dominante no mercado local.

### 5.2 O "Opportunity Score" como métrica proprietária

O artigo menciona que a Kalodata tem um "Opportunity Score" baseado em ML. Vocês já têm a base matemática para criar algo equivalente com o seu scoring determinístico — e podem ser mais transparentes sobre como ele funciona (a Kalodata é uma caixa preta). Transparência de metodologia pode ser um diferencial para creators que querem entender por que um produto é recomendado.

### 5.3 Content Angles como funcionalidade de retenção

O modelo `ContentAngle` existe no banco. Essa é a feature que transforma o produto de "dashboard de dados" em "assistente de creator". Em vez de só mostrar "produto X está em alta", mostrem: "Produto X está em alta. Ângulos de conteúdo que funcionam: (1) Review de 15 segundos focando na transformação visual, (2) Comparação antes/depois, (3) 'POV: você descobre esse produto'". Isso pode usar um LLM simples para gerar, e é o que diferencia uma ferramenta de dados de um copiloto criativo.

### 5.4 Modelo de física para previsão de tendências

Vocês mencionaram "matemática e física sofisticada". A oportunidade real está em modelar o ciclo de vida do produto como um sistema dinâmico. A curva de adoção do TikTok se parece com o modelo SIR de epidemiologia (Suscetíveis → Infectados → Recuperados). Implementem:

```
dP/dt = β * P * (N - P) / N - γ * P

Onde:
P = número de creators promovendo
N = tamanho do nicho (creators potenciais na categoria)
β = taxa de "contágio" (viralidade do produto)
γ = taxa de "recuperação" (saturação/abandono)
```

Isso permite prever QUANDO um produto vai saturar, não apenas detectar que saturou.

### 5.5 Integração com Google Trends Brasil

Vocês já têm `pytrends` no `pyproject.toml` e configs para `GOOGLE_TRENDS_GEO=BR`. Cruzar dados de busca do Google com dados do TikTok é extremamente poderoso — se um produto está ganhando tração no TikTok E mostrando crescimento no Google Trends BR, é um sinal fortíssimo de demanda genuína (não apenas viralidade efêmera).

---

## 6. ROADMAP SUGERIDO PARA O MVP

### Fase 1: Poda (1 semana)
- Remover apps/frontend, apps/website, backend/ranking_api
- Simplificar orquestração (trocar LangGraph por script sequencial)
- Ignorar AIOX framework (não precisa deletar, só parar de usar)
- Consolidar em: CLI + FastAPI + Streamlit mínimo

### Fase 2: Fortalecer o Core (2 semanas)
- Adicionar f_price (elasticidade gaussiana)
- Reformular f_competition → f_opportunity (curva assimétrica)
- Implementar estimativa de GMV via delta de inventário
- Classificador de fase do ciclo de vida (EMERGENTE → SATURADO)
- Integrar commission_rate no scoring
- Aumentar frequência para diária

### Fase 3: Diferenciação (2 semanas)
- Popular modelo Creator com dados reais da Apify
- Gerar Content Angles via LLM (OpenAI já configurado)
- Integrar Google Trends BR como sinal de validação
- Implementar modelo SIR para previsão de saturação

### Fase 4: Validação (contínua)
- Colocar na mão de 10-20 creators brasileiros
- Medir: eles voltam? Eles usam as recomendações? Eles ganham dinheiro?
- Iterar com base no feedback real

---

## 7. RESUMO EXECUTIVO

O Creator Product Radar tem uma base técnica sólida — o motor de scoring é bem pensado e o pipeline de dados funciona. O problema não é técnico, é de foco. O projeto está tentando ser muitas coisas ao mesmo tempo (framework de desenvolvimento, plataforma enterprise, dashboard operacional, site de marketing) antes de provar que a hipótese central funciona: "Conseguimos recomendar produtos lucrativos para micro-creators do TikTok Shop BR de forma consistente?"

Removam tudo que não responde essa pergunta. Adicionem o que falta do modelo de 5 etapas da Kalodata. E coloquem na mão de creators reais o mais rápido possível. A matemática elegante só importa se gera resultado real para quem usa.

---

*Documento gerado como consultoria estratégica para o projeto Creator Product Radar.*
