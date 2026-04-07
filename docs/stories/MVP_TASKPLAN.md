# MVP Task Plan — Creator Product Radar

> Plano de execução para Claude Code via terminal.
> Cada task é autocontida com: contexto, arquivos envolvidos, critérios de aceite e comando de teste.
> Copie este arquivo para o contexto do Claude Code e peça para executar task por task.

---

## FASE 0: PREPARAÇÃO E PODA (~1 dia)

### TASK 0.1 — Adicionar dependência `openai` ao projeto

**Contexto:** O projeto usa `OPENAI_API_KEY` e `OPENAI_MODEL` no `AppSettings` mas o pacote `openai` não está no `pyproject.toml`. Precisamos dele para todas as integrações com LLM.

**Arquivos:**

- `pyproject.toml` — adicionar `"openai>=1.30,<2.0"` nas dependencies

**Ação:**

```text
Adicione "openai>=1.30,<2.0" à lista de dependencies em pyproject.toml.
Rode: uv sync --cache-dir .uv-cache --all-groups
Verifique que importa corretamente: python -c "import openai; print(openai.__version__)"
```

**Critério de aceite:** `import openai` funciona sem erro.

---

### TASK 0.2 — Criar módulo compartilhado para cliente OpenAI

**Contexto:** Todos os agentes que usarão LLM precisam de um cliente OpenAI configurado. Centralize em um único módulo com retry, timeout, e fallback.

**Arquivos:**

- `services/shared/llm_client.py` — **NOVO**

**Ação:**

```text
Crie services/shared/llm_client.py com:
1. Função get_llm_client() que retorna OpenAI(api_key=settings.openai_api_key)
2. Função llm_json_call(prompt: str, temperature: float = 0.2, max_tokens: int = 400) -> dict
   - Usa settings.openai_model
   - response_format={"type": "json_object"}
   - Parse JSON da resposta
   - Try/except com retry 1x e timeout de 30s
   - Loga prompt e resposta no logger
3. Constante LLM_AVAILABLE: bool que verifica se openai_api_key está configurada
```

**Critério de aceite:** `from services.shared.llm_client import llm_json_call, LLM_AVAILABLE` funciona.

---

### TASK 0.3 — Remover backend duplicado

**Contexto:** `backend/ranking_api/` duplica funcionalidade da FastAPI em `apps/api/`. Remover para reduzir confusão.

**Arquivos:**

- `backend/` — remover diretório inteiro

**Ação:**

```text
Remova o diretório backend/ do projeto.
Verifique que nenhum import no resto do projeto referencia backend/.
Rode: uv run ruff check apps bin services scoring ranking ingestion tests
```

**Critério de aceite:** Ruff passa sem erros. Nenhum import quebrado.

---

### TASK 0.4 — Simplificar orquestração: substituir LangGraph por pipeline sequencial

**Contexto:** O LangGraph em `services/orchestration/graphs/weekly_graph.py` orquestra um pipeline 100% determinístico. Substituir por um script sequencial simples que executa as mesmas etapas. Manter a interface do `execute_weekly_run()` intacta.

**Arquivos:**

- `services/orchestration/pipeline.py` — **NOVO** (pipeline sequencial)
- `services/orchestration/weekly_run.py` — modificar para usar pipeline novo
- `services/orchestration/graphs/weekly_graph.py` — manter como referência mas não importar

**Ação:**

```text
1. Crie services/orchestration/pipeline.py com uma função execute_pipeline(session, week_start, profile)
   que executa sequencialmente:
   a. validate_inputs
   b. extract_features
   c. run_trend_agent
   d. run_viral_potential_agent
   e. run_creator_accessibility_agent
   f. aggregate_scores
   g. persist_scores
   h. finalize

2. Cada passo é uma chamada de função direta — sem grafo, sem state machine.

3. Modifique weekly_run.py para chamar execute_pipeline() em vez de build_weekly_run_graph().

4. Mantenha weekly_graph.py como arquivo de referência (não delete).
```

**Critério de aceite:**

```bash
uv run python -m bin.radar ingest-mock --profile smoke
uv run python -m bin.radar weekly-run
# Deve completar sem erros e gerar ProductScores no banco
```

---

### TASK 0.5 — Generalizar pipeline de semanal para configurável

**Contexto:** O pipeline roda apenas semanalmente. Parametrizar para rodar com qualquer frequência (diário para o MVP).

**Arquivos:**

- `services/orchestration/weekly_run.py` → renomear para `services/orchestration/run_pipeline.py`
- `bin/radar.py` — atualizar comando `weekly-run` e adicionar comando `daily-run`

**Ação:**

```text
1. Renomeie weekly_run.py para run_pipeline.py
2. Renomeie execute_weekly_run() para execute_pipeline_run()
3. Adicione parâmetro frequency: str = "weekly" (aceita "daily", "weekly")
4. Em bin/radar.py:
   - Mantenha comando "weekly-run" chamando execute_pipeline_run(frequency="weekly")
   - Adicione comando "daily-run" chamando execute_pipeline_run(frequency="daily")
   - "daily-run" usa window de 1 dia em vez de 7
5. Atualize todos os imports que referenciam weekly_run
```

**Critério de aceite:**

```bash
uv run python -m bin.radar daily-run --profile smoke
# Completa sem erros
```

---

## FASE 1: FORTALECER O MOTOR DE SCORING (~3-4 dias)

### TASK 1.1 — Adicionar fator f_price (elasticidade gaussiana)

**Contexto:** Produtos entre $15-45 USD são otimizados para compra por impulso no TikTok. Falta um fator de preço no scoring. Usar curva gaussiana centrada em $25 com sigma $12.

**Arquivos:**

- `scoring/factors.py` — adicionar `f_price()`
- `scoring/calibration.py` — adicionar `price_optimal: float = 25.0` e `price_sigma: float = 12.0`
- `scoring/models.py` — adicionar campo `price` ao `ProductSignals` se não existir
- `scoring/aggregator.py` — integrar `f_price` no cálculo com peso `w5`

**Ação:**

```text
1. Em scoring/calibration.py, adicione ao ScoringParams:
   price_optimal: float = 25.0
   price_sigma: float = 12.0

   E atualize o dict weights para ter 5 pesos:
   weights: {"w1": 0.25, "w2": 0.20, "w3": 0.20, "w4": 0.15, "w5": 0.20}

2. Em scoring/factors.py, adicione:
   def f_price(price: float, params: ScoringParams) -> float:
       optimal = params.price_optimal
       sigma = params.price_sigma
       if sigma <= 0:
           return 0.0
       return clamp_score(100.0 * exp(-0.5 * ((price - optimal) / sigma) ** 2))

3. Em scoring/aggregator.py:
   - Importe f_price
   - Adicione price_score ao score_product()
   - Inclua no base_score com peso w5
   - Adicione price_score ao ProductScore

4. Em scoring/models.py, certifique-se que ProductSignals tem campo price: float
```

**Critério de aceite:**

```bash
uv run pytest tests/unit/ -q
# f_price(25.0, params) ≈ 100.0 (centro da gaussiana)
# f_price(10.0, params) ≈ 24.4 (fora do sweet spot)
# f_price(40.0, params) ≈ 24.4 (simétrico)
```

---

### TASK 1.2 — Reformular f_competition → f_opportunity (curva assimétrica)

**Contexto:** Atualmente `f_competition` é logística invertida: menos criadores = melhor. Mas o método de 5 etapas da Kalodata ensina que o ideal é 5-15 criadores (validação de replicabilidade). Zero = não testado, 1 = dependência, >80 = saturado.

**Arquivos:**

- `scoring/factors.py` — reescrever `f_competition` como `f_opportunity`
- `scoring/calibration.py` — adicionar `creator_sweet_spot: float = 10.0`
- `scoring/aggregator.py` — atualizar referência

**Ação:**

```text
1. Em scoring/calibration.py, adicione:
   creator_sweet_spot: float = 10.0

2. Em scoring/factors.py, substitua f_competition por:
   def f_opportunity(n: float, params: ScoringParams) -> float:
       """Score creator opportunity window.
       Asymmetric curve: ramp up to sweet spot, then logistic decay.
       """
       sweet = params.creator_sweet_spot
       n = max(0.0, n)
       if sweet <= 0:
           return 0.0
       if n <= sweet:
           return clamp_score(100.0 * (n / sweet) ** 0.6)
       return clamp_score(100.0 / (1.0 + exp(params.alpha * (n - params.n0))))

3. Em scoring/aggregator.py:
   - Substitua f_competition por f_opportunity
   - Renomeie competition_score para opportunity_score

4. Atualize todos os testes que referenciam f_competition
```

**Critério de aceite:**

```bash
uv run pytest tests/unit/ -q
# f_opportunity(0) ≈ 0 (não testado)
# f_opportunity(10) ≈ 100 (sweet spot)
# f_opportunity(5) ≈ 76 (validado mas sub-ótimo)
# f_opportunity(80) → baixo (saturado)
```

---

### TASK 1.3 — Integrar commission_rate no scoring

**Contexto:** `commission_rate` é coletado na ingestão e validado como > 0, mas NÃO é usado no scoring. Para creators, a comissão é o fator mais importante — determina quanto ganham.

**Arquivos:**

- `scoring/factors.py` — adicionar `f_commission()`
- `scoring/calibration.py` — adicionar parâmetros
- `scoring/aggregator.py` — integrar no `estimated_revenue_signal()`
- `scoring/models.py` — garantir que `ProductSignals` tem `commission_rate`

**Ação:**

```text
1. No estimated_revenue_signal() em aggregator.py, a commission_rate JÁ é usada:
   estimated_commission = signals.price * signals.commission_rate
   Verifique que commission_rate está sendo passada corretamente do banco para ProductSignals.

2. Adicione um BOOST no f_revenue baseado em commission_rate alta:
   - commission_rate >= 20%: boost de 1.2x no revenue_score
   - commission_rate >= 30%: boost de 1.4x
   Isso reflete que alta comissão é diretamente mais lucrativa para o creator.

3. Certifique-se que o feature_extraction em services/workers/ extrai
   commission_rate do ProductSnapshot e persiste como ProductSignal.
```

**Critério de aceite:**

```bash
uv run pytest tests/unit/ -q
# Produto com commission_rate=30% deve ter revenue_score maior que produto idêntico com 10%
```

---

### TASK 1.4 — Implementar classificador de fase do ciclo de vida

**Contexto:** Em vez de apenas um score numérico, classificar o produto em fases acionáveis: EMERGENTE, ACELERANDO, PICO, SATURADO. Baseado no método de 5 etapas da Kalodata.

**Arquivos:**

- `scoring/lifecycle.py` — **NOVO**
- `scoring/aggregator.py` — chamar classificador e incluir no ProductScore
- `scoring/models.py` — adicionar campo `lifecycle_phase` ao ProductScore
- `services/shared/db/models.py` — adicionar coluna `lifecycle_phase` ao ProductScore do banco

**Ação:**

```text
1. Crie scoring/lifecycle.py:
   def classify_lifecycle(
       growth_7d: float,
       active_creators: int,
       days_since_detected: int,
       growth_3d: float = 0.0,
   ) -> str:
       # Crescimento negativo ou >80 criadores → SATURADO
       if growth_7d < 0 or active_creators > 80:
           return "SATURADO"
       # Crescimento desacelerando (3d < 7d) e muitos criadores → PICO
       if active_creators > 30 and growth_3d < growth_7d:
           return "PICO"
       # Crescimento >500% e 10-30 criadores → ACELERANDO
       if growth_7d > 500 and 10 <= active_creators <= 30:
           return "ACELERANDO"
       # Crescimento 200-500%, <10 criadores, <14 dias → EMERGENTE
       if 200 <= growth_7d <= 500 and active_creators < 10 and days_since_detected < 14:
           return "EMERGENTE"
       # Crescimento alto mas fora dos critérios → ACELERANDO
       if growth_7d > 200 and active_creators < 30:
           return "ACELERANDO"
       # Default
       if active_creators < 10:
           return "EMERGENTE"
       return "PICO"

2. Em scoring/aggregator.py, chame classify_lifecycle() e inclua no ProductScore.

3. Crie migração Alembic para adicionar coluna lifecycle_phase ao product_scores.
```

**Critério de aceite:**

```bash
uv run pytest tests/unit/ -q
# classify_lifecycle(growth_7d=300, creators=5, days=7) == "EMERGENTE"
# classify_lifecycle(growth_7d=600, creators=20, days=10) == "ACELERANDO"
# classify_lifecycle(growth_7d=-10, creators=90, days=30) == "SATURADO"
```

---

### TASK 1.5 — Implementar estimativa de GMV via delta de inventário

**Contexto:** A Kalodata estima GMV capturando estoque em T1, estoque em T2, calculando delta e multiplicando pelo preço. O `ProductSnapshot` já tem `raw_payload` que pode conter dados de estoque.

**Arquivos:**

- `scoring/gmv_estimator.py` — **NOVO**
- `services/workers/feature_extraction.py` — extrair stock_count do raw_payload como ProductSignal
- `scoring/aggregator.py` — usar GMV estimado no scoring

**Ação:**

```text
1. Crie scoring/gmv_estimator.py:
   from decimal import Decimal

   def estimate_gmv_from_snapshots(
       snapshots: list[dict],  # ordenados por captured_at
   ) -> Decimal | None:
       """Estima GMV via delta de inventário entre snapshots consecutivos.

       Retorna None se não há dados suficientes.
       Caveat: reposições, carrinhos abandonados e remoções manuais distorcem.
       """
       if len(snapshots) < 2:
           return None

       total_gmv = Decimal("0")
       for i in range(1, len(snapshots)):
           prev_stock = snapshots[i-1].get("stock_count")
           curr_stock = snapshots[i].get("stock_count")
           price = snapshots[i].get("price")

           if prev_stock is None or curr_stock is None or price is None:
               continue

           delta = max(0, prev_stock - curr_stock)  # só contabiliza reduções
           total_gmv += Decimal(str(delta)) * Decimal(str(price))

       return total_gmv if total_gmv > 0 else None

2. Em feature_extraction.py, extraia "stock_count" do raw_payload se disponível
   e persista como ProductSignal com signal_name="stock_count".

3. No relatório (services/reporting/builder.py), inclua gmv_estimate com caveat:
   "Estimativa direcional — reposições e carrinhos abandonados podem distorcer."
```

**Critério de aceite:**

```bash
uv run pytest tests/unit/ -q
# estimate_gmv([{stock: 5000, price: 20}, {stock: 4500, price: 20}]) == Decimal("10000")
# estimate_gmv([{stock: 4500, price: 20}, {stock: 5000, price: 20}]) == Decimal("0")  # reposição ignorada
```

---

## FASE 2: INTEGRAR IA NOS AGENTES (~4-5 dias)

### TASK 2.1 — Reescrever viral_potential_agent com LLM + fallback

**Contexto:** O agente atual usa 8 keywords hardcoded para avaliar viralidade visual. Substituir `visual_component` e `hook_component` por avaliação via LLM, mantendo `shareability_component` determinístico e fallback para heurística atual.

**Arquivos:**

- `services/agents/runtime/viral_potential_agent.py` — reescrever
- `services/agents/prompts/viral_assessment.py` — **NOVO** (prompt template)

**Ação:**

```text
1. Crie services/agents/prompts/viral_assessment.py com o VIRAL_ASSESSMENT_PROMPT
   conforme descrito em docs/AI_INTEGRATION_STRATEGY.md seção 1.

2. Em viral_potential_agent.py:
   a. Mantenha TODA a lógica de heurística atual como funções privadas (_resolve_visual_component_seed, etc.)
   b. Adicione async def _evaluate_with_llm(agent_input) -> dict que chama llm_json_call()
   c. Modifique evaluate_viral_potential_input():
      - Se LLM_AVAILABLE: tenta LLM, fallback para heurística
      - Se não LLM_AVAILABLE: usa heurística diretamente
   d. Shareability_component SEMPRE determinístico
   e. Clamp todos os valores do LLM: max(0, min(40, llm_result["visual_demo_score"]))
   f. Salve o resultado do LLM no evidence da AgentReasoning

3. Adicione cache simples: dict[str, dict] no módulo, keyed por (product_id, date.today())
```

**Critério de aceite:**

```bash
# Com OPENAI_API_KEY configurada:
uv run python -m bin.radar ingest-mock --profile smoke && uv run python -m bin.radar weekly-run
# Pipeline completa com scores de viralidade gerados via LLM

# Sem OPENAI_API_KEY:
# Pipeline completa usando fallback heurístico (comportamento atual)
```

---

### TASK 2.2 — Reescrever creator_accessibility_agent com LLM + fallback

**Contexto:** Similar à task 2.1. O agente usa 8 `_AUTHORITY_RISK_KEYWORDS` para penalizar produtos difíceis. Substituir `authority_component` e `audience_fit_component` por LLM, mantendo `price_friction_component` determinístico.

**Arquivos:**

- `services/agents/runtime/creator_accessibility_agent.py` — reescrever
- `services/agents/prompts/accessibility_assessment.py` — **NOVO**

**Ação:**

```text
1. Crie services/agents/prompts/accessibility_assessment.py com ACCESSIBILITY_PROMPT
   conforme docs/AI_INTEGRATION_STRATEGY.md seção 3.

2. Em creator_accessibility_agent.py:
   a. Mantenha heurística atual como fallback
   b. Adicione _evaluate_with_llm(agent_input) usando llm_json_call()
   c. LLM retorna: authority_needed (0-25), audience_fit (0-40), barriers[]
   d. price_friction_component: SEMPRE _price_component() determinístico
   e. Clamp LLM values, cache por (product_id, date)
```

**Critério de aceite:**

```bash
uv run python -m bin.radar weekly-run
# Accessibility scores refletem julgamento contextual, não apenas keywords
```

---

### TASK 2.3 — Implementar gerador de Content Angles via LLM

**Contexto:** A tabela `content_angles` existe no banco mas está vazia. Gerar ângulos de conteúdo via LLM para os top N produtos após o scoring.

**Arquivos:**

- `services/agents/runtime/content_angle_generator.py` — **NOVO**
- `services/agents/prompts/content_angles.py` — **NOVO**
- `services/orchestration/pipeline.py` — adicionar step de geração de angles

**Ação:**

```text
1. Crie services/agents/prompts/content_angles.py com CONTENT_ANGLE_PROMPT
   conforme docs/AI_INTEGRATION_STRATEGY.md seção 2.

2. Crie services/agents/runtime/content_angle_generator.py:
   async def generate_angles_for_product(
       product_id, title, category, price,
       viral_score, accessibility_score, classification,
       strengths, run_id, week_start, session
   ) -> list[ContentAngle]:
       - Chama llm_json_call() com temperature=0.7
       - Parseia 3 ângulos do JSON
       - Cria objetos ContentAngle (modelo do banco já existe)
       - Persiste no banco via session
       - Retorna lista de ContentAngle

   async def generate_angles_for_top_products(
       session, run_id, week_start, limit=20
   ):
       - Query ProductScore WHERE classification IN ("EXPLOSIVE", "HIGH")
       - Para cada produto: generate_angles_for_product()
       - Log total de ângulos gerados

3. Em services/orchestration/pipeline.py:
   - Após persist_scores, adicione step generate_content_angles
   - Apenas se LLM_AVAILABLE
```

**Critério de aceite:**

```bash
uv run python -m bin.radar weekly-run
# Verificar no banco: SELECT count(*) FROM content_angles; -- deve ser > 0
# Verificar: SELECT hook_text, angle_type FROM content_angles LIMIT 5;
```

---

### TASK 2.4 — Adicionar resumo explicativo em linguagem humana

**Contexto:** Creators não querem ver "score 87, trend 42, viral 35". Querem "Este produto está explodindo porque tem alta transformação visual e poucos creators promovendo. Janela de oportunidade estimada: 2 semanas."

**Arquivos:**

- `services/agents/prompts/product_summary.py` — **NOVO**
- `services/agents/runtime/summary_generator.py` — **NOVO**
- `services/reporting/builder.py` — integrar resumo no relatório
- `apps/api/schemas.py` — adicionar campo `summary_text` ao response

**Ação:**

```text
1. Crie prompt em services/agents/prompts/product_summary.py:
   PRODUCT_SUMMARY_PROMPT que recebe: título, scores, classificação, lifecycle_phase,
   strengths, weaknesses, e gera um resumo de 2-3 frases em português BR coloquial.

2. Crie services/agents/runtime/summary_generator.py:
   async def generate_summary(product_data: dict) -> str
   - temperature=0.4 (meio-termo entre consistência e naturalidade)
   - Fallback: gera template string com os dados se LLM falhar

3. Integre no builder.py e nos schemas da API.
```

**Critério de aceite:**

```bash
uv run python -m bin.radar export-report --limit 5
# Cada produto no relatório deve ter um campo "summary" em português
```

---

## FASE 3: MODELO DE FÍSICA E DADOS DE CREATORS (~4-5 dias)

### Checklist da fase 3

- [x] TASK 3.1 — Implementar modelo SIR de saturação
- [x] TASK 3.2 — Popular modelo Creator com dados da Apify
- [x] TASK 3.3 — Integrar Google Trends BR como sinal de validação

### File List da fase 3

- `scoring/saturation_model.py`
- `services/agents/prompts/saturation_params.py`
- `services/agents/runtime/saturation_agent.py`
- `services/ingestion/adapters/creator_extractor.py`
- `services/shared/db/models.py`
- `services/workers/google_trends.py`
- `services/workers/feature_extraction.py`
- `services/scoring/aggregation.py`
- `scoring/aggregator.py`
- `bin/radar.py`
- `infra/migrations/versions/20260330_0002_add_creator_products.py`

### TASK 3.1 — Implementar modelo SIR de saturação

**Contexto:** Modelar ciclo de vida como sistema epidemiológico. LLM estima β e γ. Simulação numérica é determinística.

**Arquivos:**

- `scoring/saturation_model.py` — **NOVO**
- `services/agents/prompts/saturation_params.py` — **NOVO**
- `services/agents/runtime/saturation_agent.py` — **NOVO**

**Ação:**

```text
1. Crie scoring/saturation_model.py conforme docs/AI_INTEGRATION_STRATEGY.md seção 4:
   - simulate_sir(current_creators, niche_size, beta, gamma, days_ahead=30) -> list[dict]
   - _classify_phase(P, N, dP) -> str
   - estimate_opportunity_window(trajectory) -> int | None (dias até >60% saturação)

2. Crie services/agents/prompts/saturation_params.py com SATURATION_PARAMS_PROMPT

3. Crie services/agents/runtime/saturation_agent.py:
   - estimate_saturation_params(agent_input) -> dict com beta, gamma via LLM
   - Fallback: beta=0.15, gamma=0.05 (valores conservadores)
   - Chama simulate_sir() com os parâmetros
   - Retorna trajectory + opportunity_window

4. Integre no pipeline: após scoring, para top 50 produtos, estimar saturação
```

**Critério de aceite:**

```bash
uv run pytest tests/unit/ -q
# simulate_sir(creators=5, niche=200, beta=0.2, gamma=0.05, days=30)
# Deve retornar trajetória com fases EMERGENTE → ACELERANDO → PICO
# estimate_opportunity_window deve retornar um inteiro de dias
```

---

### TASK 3.2 — Popular modelo Creator com dados da Apify

**Contexto:** O modelo `Creator` existe no banco com handle, tier, primary_niche, region — mas está vazio. Os dados da Apify via `clockworks/tiktok-scraper` trazem informações de criadores nos vídeos.

**Arquivos:**

- `services/ingestion/adapters/creator_extractor.py` — **NOVO**
- `services/shared/db/models.py` — adicionar relação Creator ↔ Product (tabela pivot)
- Nova migração Alembic para tabela `creator_products`

**Ação:**

```text
1. Crie services/ingestion/adapters/creator_extractor.py:
   def extract_creators_from_video_payload(raw_payload: dict) -> list[dict]:
       - Extrai handle, follower_count, niche (do conteúdo do vídeo)
       - Retorna lista de dicts com dados do creator

   def persist_creators(session, creators: list[dict], product_id: str):
       - Upsert Creator por handle
       - Criar relação creator_products

2. Crie migração Alembic para tabela creator_products:
   - creator_id FK → creators.id
   - product_id FK → products.id
   - first_seen_at, last_seen_at
   - Unique constraint (creator_id, product_id)

3. No pipeline de ingestão (services/ingestion/service.py):
   - Após ingerir produto, chamar extract_creators_from_video_payload
   - Persistir creators e relações
```

**Critério de aceite:**

```bash
uv run python -m bin.radar ingest-apify --keywords "led strip"
# SELECT count(*) FROM creators; -- deve ser > 0
# SELECT count(*) FROM creator_products; -- deve ter relações
```

---

### TASK 3.3 — Integrar Google Trends BR como sinal de validação

**Contexto:** `pytrends` já está no pyproject.toml. `GOOGLE_TRENDS_GEO=BR` está configurado. Cruzar tendências Google com dados TikTok valida demanda genuína.

**Arquivos:**

- `services/workers/google_trends.py` — **NOVO**
- `services/workers/feature_extraction.py` — chamar google_trends como sinal adicional

**Ação:**

```text
1. Crie services/workers/google_trends.py:
   from pytrends.request import TrendReq

   def fetch_trend_score(keyword: str, geo: str = "BR", timeframe: str = "now 7-d") -> int | None:
       """Retorna interest score (0-100) do Google Trends para o keyword.
       Retorna None se falhar (rate limit, keyword sem dados, etc.)."""
       try:
           pytrends = TrendReq(hl="pt-BR")
           pytrends.build_payload([keyword], geo=geo, timeframe=timeframe)
           data = pytrends.interest_over_time()
           if data.empty:
               return None
           return int(data[keyword].iloc[-1])
       except Exception:
           return None

2. Em feature_extraction.py:
   - Para cada produto, extrair keyword principal do título
   - Chamar fetch_trend_score()
   - Persistir como ProductSignal(signal_name="google_trends_score")
   - Rate limit: max 1 request por 2 segundos (Google Trends throttle)

3. No scoring, usar google_trends_score como validação cruzada:
   - Se google_trends_score > 50 E trend_score > 70: boost de 1.1x no final_score
   - Isso confirma que a tendência TikTok tem demanda real fora da plataforma
```

**Critério de aceite:**

```bash
uv run python -c "from services.workers.google_trends import fetch_trend_score; print(fetch_trend_score('escova alisadora'))"
# Deve retornar um número entre 0-100 ou None
```

---

## FASE 4: API E RELATÓRIOS (~2-3 dias)

### Checklist da fase 4

- [x] TASK 4.1 — Atualizar endpoints da API com novos campos
- [x] TASK 4.2 — Atualizar relatório com disclaimer de estimativa

### File List da fase 4

- `apps/api/schemas.py`
- `apps/api/main.py`
- `services/reporting/read_service.py`
- `services/reporting/builder.py`
- `apps/api/ranking_api/service.py`
- `apps/frontend/src/types/api.ts`
- `tests/integration/test_api_read_endpoints.py`
- `tests/integration/test_report_builder.py`
- `tests/smoke/test_cli_weekly_run.py`
- `tests/unit/test_report_builder.py`

### TASK 4.1 — Atualizar endpoints da API com novos campos

**Contexto:** Novos campos foram adicionados: lifecycle_phase, content_angles, opportunity_window, google_trends_score, summary_text. A API precisa expô-los.

**Arquivos:**

- `apps/api/schemas.py` — adicionar campos novos aos responses
- `apps/api/main.py` — atualizar endpoints
- `services/reporting/read_service.py` — incluir novos dados nas queries

**Ação:**

```text
1. Em schemas.py, atualize:
   RankingResponse: adicionar lifecycle_phase, opportunity_window_days
   ProductDetailResponse: adicionar lifecycle_phase, content_angles, summary_text,
                          google_trends_score, gmv_estimate, opportunity_window_days

2. Em read_service.py:
   - list_weekly_ranking: incluir lifecycle_phase no JOIN
   - get_product_detail: incluir content_angles e saturation data

3. Em main.py, endpoint GET /products/{product_id}/content-angles:
   - Retornar angles reais do banco (não mais stub)
```

**Critério de aceite:**

```bash
uv run uvicorn apps.api.main:app --port 8000 &
curl http://localhost:8000/rankings | python -m json.tool
# Deve mostrar lifecycle_phase em cada produto
curl http://localhost:8000/products/{id}/content-angles | python -m json.tool
# Deve retornar ângulos de conteúdo reais
```

---

### TASK 4.2 — Atualizar relatório com disclaimer de estimativa

**Contexto:** O artigo da Kalodata ensina: "Contexto direcional, não contabilidade exata". O relatório deve ser honesto sobre limitações.

**Arquivos:**

- `services/reporting/builder.py` — adicionar disclaimers e novos campos

**Ação:**

```text
1. No build_report_payload(), adicione ao JSON:
   - "methodology_disclaimer": "Scores são estimativas direcionais baseadas em sinais
     públicos. GMV estimado NÃO é lucro real — reposições de estoque, devoluções e
     carrinhos abandonados podem distorcer os números. Use como bússola, não como GPS."
   - "data_freshness": "Dados atualizados a cada {frequency}. Tendências no TikTok
     saturam em dias — aja rápido sobre produtos EMERGENTES."

2. Para cada produto no relatório, inclua:
   - lifecycle_phase
   - opportunity_window_days (se disponível)
   - content_angles (top 3)
   - gmv_estimate (com caveat)
   - google_trends_validation: true/false
```

**Critério de aceite:**

```bash
uv run python -m bin.radar export-report --limit 5
# JSON deve conter methodology_disclaimer e lifecycle_phase por produto
```

---

## FASE 5: TESTES E QUALIDADE (~2 dias)

### Checklist da fase 5

- [x] TASK 5.1 — Escrever testes unitários para novos fatores de scoring
- [x] TASK 5.2 — Atualizar smoke tests para novo pipeline
- [x] TASK 5.3 — Rodar suite completa de qualidade

### File List da fase 5

- `tests/unit/test_factors.py`
- `tests/unit/test_lifecycle.py`
- `tests/unit/test_gmv_estimator.py`
- `tests/unit/test_saturation_model.py`
- `tests/smoke/test_cli_weekly_run.py`
- `pyproject.toml`
- `services/shared/llm_client.py`
- `tests/integration/test_weekly_graph.py`

### TASK 5.1 — Escrever testes unitários para novos fatores de scoring

**Arquivos:**

- `tests/unit/test_factors.py` — adicionar testes para f_price e f_opportunity
- `tests/unit/test_lifecycle.py` — **NOVO**
- `tests/unit/test_gmv_estimator.py` — **NOVO**
- `tests/unit/test_saturation_model.py` — **NOVO**

**Ação:**

```text
Escreva testes para:

1. f_price:
   - Centro da gaussiana (price=25) → ≈100
   - Extremo barato (price=5) → <30
   - Extremo caro (price=80) → <10
   - Price=0 → score baixo
   - Preço negativo → tratado gracefully

2. f_opportunity:
   - n=0 → 0 (não testado)
   - n=sweet_spot → 100 (ideal)
   - n=sweet_spot/2 → entre 50-80
   - n=100 → baixo (saturado)
   - n=-1 → tratado como 0

3. classify_lifecycle:
   - Todos os 4 estados com inputs claros
   - Edge cases (growth=0, creators=0, days=0)

4. estimate_gmv_from_snapshots:
   - 2 snapshots com redução → GMV positivo
   - 2 snapshots com aumento → GMV zero (reposição)
   - 1 snapshot → None
   - Snapshots sem price → None

5. simulate_sir:
   - Parâmetros normais → trajetória crescente depois estabilizando
   - beta=0 → sem crescimento
   - gamma muito alto → decay rápido
```

**Critério de aceite:**

```bash
uv run pytest tests/unit/ -q
# Todos passam
uv run ruff check scoring/ tests/
# Sem erros de lint
```

---

### TASK 5.2 — Atualizar smoke tests para novo pipeline

**Arquivos:**

- `tests/smoke/` — atualizar para refletir novo pipeline sequencial e novos campos

**Ação:**

```text
Atualize os smoke tests para:
1. Pipeline sequencial (sem LangGraph)
2. Comando daily-run
3. Novos campos no ProductScore (lifecycle_phase, price_score, opportunity_score)
4. Content angles sendo gerados (se LLM_AVAILABLE)
5. Relatório com disclaimer

Rode:
uv run pytest tests/smoke/ -q
```

**Critério de aceite:**

```bash
uv run pytest tests/smoke/ -q
# Todos passam
```

---

### TASK 5.3 — Rodar suite completa de qualidade

**Ação:**

```bash
uv run ruff check apps bin services scoring ranking ingestion tests
uv run ruff format .
uv run mypy apps bin services scoring ranking ingestion tests
uv run pytest -q
```

**Critério de aceite:** Tudo verde. Zero erros.

---

## RESUMO DE DEPENDÊNCIAS ENTRE TASKS

```text
FASE 0 (Preparação):
  0.1 (openai) ──→ 0.2 (llm_client) ──→ FASE 2 (todas as tasks de IA)
  0.3 (remover backend) ──→ independente
  0.4 (pipeline sequencial) ──→ 0.5 (frequência configurável)

FASE 1 (Scoring):
  1.1 (f_price) ──→ independente de 1.2
  1.2 (f_opportunity) ──→ independente de 1.1
  1.3 (commission_rate) ──→ independente
  1.4 (lifecycle) ──→ depende de 1.2 (usa active_creators)
  1.5 (GMV) ──→ independente

FASE 2 (IA):
  2.1 (viral LLM) ──→ depende de 0.2
  2.2 (accessibility LLM) ──→ depende de 0.2
  2.3 (content angles) ──→ depende de 0.2 + 2.1 scores
  2.4 (resumo) ──→ depende de 0.2

FASE 3 (Física + Dados):
  3.1 (SIR) ──→ depende de 0.2 + 1.4
  3.2 (Creators) ──→ independente
  3.3 (Google Trends) ──→ independente

FASE 4 (API):
  4.1 ──→ depende de TODAS as fases anteriores
  4.2 ──→ depende de 4.1

FASE 5 (Testes):
  5.1 ──→ depende de FASE 1
  5.2 ──→ depende de FASE 0 + FASE 1
  5.3 ──→ depende de TUDO
```

---

## COMO USAR COM CLAUDE CODE

Para cada task, copie o bloco inteiro e cole no Claude Code com o prefixo:

```text
Execute a TASK X.Y do plano MVP. Aqui está o contexto:
[cola o bloco da task]
```

Ou para rodar o plano completo em sequência:

```text
Leia o arquivo docs/stories/MVP_TASKPLAN.md e execute as tasks na ordem,
começando pela TASK 0.1. Após cada task, rode o critério de aceite.
Se passar, avance para a próxima. Se falhar, corrija antes de avançar.
```

---

*Plano gerado em 30/03/2026 baseado nos documentos:*
*- docs/ADVISORY_MVP_STRATEGY.md*
*- docs/AI_INTEGRATION_STRATEGY.md*
