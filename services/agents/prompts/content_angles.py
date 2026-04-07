"""Prompt template for LLM-based content angle generation."""

CONTENT_ANGLE_PROMPT = (
    "Voce e um estrategista de conteudo para creators pequenos do TikTok Shop Brasil.\n\n"
    "PRODUTO: {title}\n"
    "CATEGORIA: {category}\n"
    "PRECO: R$ {price}\n"
    "SCORE DE VIRALIDADE: {viral_score}/100\n"
    "SCORE DE ACESSIBILIDADE: {accessibility_score}/100\n"
    "CLASSIFICACAO: {classification}\n"
    "PONTOS FORTES: {strengths}\n\n"
    "Gere 3 angulos de conteudo para um creator com 1K-10K seguidores.\n\n"
    "Responda APENAS com JSON valido:\n"
    "{{\n"
    '  "angles": [\n'
    "    {{\n"
    '      "type": "<review|antes_depois|pov|unboxing|comparacao|tutorial_rapido|storytelling>",\n'
    '      "hook_text": "<frase de abertura do video, max 15 palavras, em portugues BR>",\n'
    '      "script_outline": "<3 bullets descrevendo a estrutura do video de 15-30s>",\n'
    '      "rationale": "<1 frase: por que esse angulo funciona para esse produto>"\n'
    "    }}\n"
    "  ]\n"
    "}}\n\n"
    "REGRAS:\n"
    "- Hooks devem ser em portugues brasileiro coloquial\n"
    "- Assuma que o creator nao tem estudo profissional (filma no celular)\n"
    "- Priorize formatos que funcionam com 0 investimento em producao\n"
    "- Cada angulo deve ser testavel em 1 hora de trabalho\n"
)
