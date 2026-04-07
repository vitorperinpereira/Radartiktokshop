"""Prompt template for estimating SIR saturation parameters."""

SATURATION_PARAMS_PROMPT = (
    "Voce e um analista de saturacao de nicho para creators do TikTok Shop Brasil.\n\n"
    "PRODUTO: {title}\n"
    "CATEGORIA: {category}\n"
    "SUBCATEGORIA: {subcategory}\n"
    "FASE DE CICLO DE VIDA: {lifecycle_phase}\n"
    "CREATORS ATIVOS: {current_creators}\n"
    "TAMANHO ESTIMADO DO NICHO: {niche_size}\n"
    "CONTEXTO: {context}\n\n"
    "Estime os parametros do modelo SIR com base neste produto.\n"
    "Responda APENAS com JSON valido:\n"
    "{{\n"
    '  "beta": 0.15,\n'
    '  "gamma": 0.05,\n'
    '  "reasoning": "curta justificativa em portugues BR"\n'
    "}}\n\n"
    "REGRAS:\n"
    "- beta e gamma devem ser positivos e coerentes com um nicho de creators\n"
    "- beta maior quando o produto espalha rapido entre creators\n"
    "- gamma maior quando o interesse perde folego rapido\n"
)
