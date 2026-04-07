"""Prompt template for LLM-based creator accessibility assessment."""

ACCESSIBILITY_PROMPT = """Voce e um analista de creator-fit do TikTok Shop Brasil.

Avalie se um creator pequeno (1K-10K seguidores) consegue vender este produto com
credibilidade sem ser especialista.

PRODUTO: {title}
CATEGORIA: {category}
SUBCATEGORIA: {subcategory}
PRECO: R$ {price}
CONTEXTO: {context}

Responda APENAS com JSON valido:
{{
  "authority_needed": <0-25>,
  "authority_reasoning": "<1 frase: que tipo de autoridade e necessaria, se alguma>",
  "audience_fit": <0-40>,
  "audience_reasoning": "<1 frase: para que tipo de audiencia esse produto funciona>",
  "barriers": ["<barreira 1>", "<barreira 2>"]
}}

Escala authority_needed (0 = qualquer pessoa vende, 25 = precisa de especialista):
- 0-8: Produto universalmente demonstravel
- 9-16: Precisa de algum contexto, mas nao expertise
- 17-25: Exige credibilidade profissional
"""
