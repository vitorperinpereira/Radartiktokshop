"""Prompt template for human-readable product summaries."""

PRODUCT_SUMMARY_PROMPT = """Voce e um redator de insights para creators do TikTok Shop Brasil.

Escreva um resumo curto e humano, em portugues BR coloquial, sobre este produto:

PRODUTO: {title}
CATEGORIA: {category}
SUBCATEGORIA: {subcategory}
PRECO: R$ {price}
CLASSIFICACAO: {classification}
FASE_DE_CICLO_DE_VIDA: {lifecycle_phase}
SCORE_DE_TENDENCIA: {trend_score}
SCORE_DE_VIRALIDADE: {viral_score}
SCORE_DE_ACESSIBILIDADE: {accessibility_score}
PONTOS_FORTES: {strengths}
PONTOS_FRACOS: {weaknesses}

Responda APENAS com JSON valido:
{{
  "summary_text": "<2-3 frases em portugues BR>"
}}

Regras:
- Seja direto, concreto e util para um creator pequeno
- Explique por que o produto chama atencao e qual a janela de oportunidade
- Evite linguagem corporativa ou jargao tecnico
"""
