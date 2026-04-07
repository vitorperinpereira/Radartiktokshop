"""Prompt template for LLM-based viral assessment."""

VIRAL_ASSESSMENT_PROMPT = """Voce e um analista de conteudo do TikTok Shop Brasil.

Avalie este produto para criacao de conteudo curto (15-60 segundos):

PRODUTO: {title}
CATEGORIA: {category}
SUBCATEGORIA: {subcategory}
PRECO: R$ {price}
CONTEXTO: {description_snippet}

Responda APENAS com JSON valido:
{{
  "visual_demo_score": <0-40>,
  "visual_reasoning": "<1 frase: por que e/nao e visual>",
  "hook_score": <0-35>,
  "hook_reasoning": "<1 frase: qual gancho funciona ou por que e dificil>",
  "suggested_format": "<review|antes_depois|pov|unboxing|comparacao|tutorial_rapido>",
  "confidence": <0.0-1.0>
}}

Criteria for visual_demo_score (0-40):
- 30-40: Transformacao visivel clara, efeito imediato na camera
- 20-29: Demonstravel mas sem wow factor visual instantaneo
- 10-19: Precisa de explicacao verbal, pouco visual
- 0-9: Dificil de demonstrar em video curto

Criteria for hook_score (0-35):
- 25-35: Gera curiosidade instantanea, "eu preciso disso" imediato
- 15-24: Interessante mas precisa de contexto
- 5-14: Generico, dificil de diferenciar
- 0-4: Sem gancho obvio para conteudo curto
"""
