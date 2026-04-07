"""Product Drilldown page for the dashboard."""

from __future__ import annotations

import streamlit as st

from apps.dashboard.read_adapter import (
    AgentReasoningView,
    extract_agent_reasoning,
    extract_explanation,
    load_product_detail,
    load_rankings,
    product_option_label,
)

st.set_page_config(page_title="Detalhes do Produto", page_icon="🔍", layout="wide")


def _format_score(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.1f}/100"


def _format_currency(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"R$ {value:.2f}"


def _format_number(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.2f}"


def _format_classification(value: str | None) -> str:
    if value is None:
        return "n/a"
    _labels: dict[str, str] = {
        "strong_weekly_bet": "Aposta da Semana",
        "test_selectively": "Testar com Cautela",
        "explosive": "Explosivo",
        "high": "Alto Potencial",
        "medium": "Médio Potencial",
        "low": "Baixo Potencial",
    }
    return _labels.get(value.lower(), value.replace("_", " ").title())


def _render_bullet_list(items: list[str], *, empty_message: str) -> None:
    if not items:
        st.caption(empty_message)
        return

    for item in items:
        st.markdown(f"- {item}")


def _render_agent_reasoning(section: AgentReasoningView, *, empty_message: str) -> None:
    if section.summary is not None:
        st.write(section.summary)
    else:
        st.caption(empty_message)

    if section.signal_breakdown:
        st.json(section.signal_breakdown)

    st.write("**Pontos Fortes**")
    _render_bullet_list(section.strengths, empty_message="Nenhum ponto forte registrado.")

    st.write("**Pontos Fracos**")
    _render_bullet_list(
        section.weaknesses,
        empty_message="Nenhum ponto fraco registrado.",
    )

    st.write("**Evidências**")
    _render_bullet_list(section.evidence, empty_message="Nenhuma evidência registrada.")


st.title("🔍 Detalhes do Produto")
st.markdown("Análise detalhada das evidências e do raciocínio dos agentes para o score do produto.")

ranking_result = load_rankings()
if ranking_result.error is not None:
    st.error(ranking_result.error)
    st.stop()

ranking = ranking_result.data
if ranking is None or ranking.count == 0:
    st.info("Nenhum produto pontuado disponível ainda. Execute o pipeline semanal primeiro.")
    st.stop()

product_ids = [item.product_id for item in ranking.items]
labels = {item.product_id: product_option_label(item) for item in ranking.items}
current_product_id = st.session_state.get("selected_product_id")
default_index = 0
if isinstance(current_product_id, str) and current_product_id in labels:
    default_index = product_ids.index(current_product_id)

selected_product_id = st.selectbox(
    "Selecione um produto para ver os detalhes:",
    options=product_ids,
    index=default_index,
    format_func=lambda product_id: labels[product_id],
)
st.session_state["selected_product_id"] = selected_product_id

selected_week_start = st.session_state.get("selected_week_start")
detail_result = load_product_detail(
    selected_product_id,
    week_start=selected_week_start if isinstance(selected_week_start, str) else None,
)

if detail_result.error is not None:
    st.error(detail_result.error)
    st.stop()

if detail_result.missing or detail_result.data is None:
    st.warning("Nenhum detalhe encontrado para o produto e semana selecionados.")
    st.stop()

detail = detail_result.data
explanation = extract_explanation(detail)
agent_reasoning = extract_agent_reasoning(detail)

st.header(detail.product.title)
st.caption(
    f"ID do Produto: {detail.product.id} | Semana: {detail.score.week_start} | "
    f"Status: {detail.product.status}"
)

metadata_columns = st.columns(4)
with metadata_columns[0]:
    st.metric("Marca", detail.product.brand or "Desconhecida")
with metadata_columns[1]:
    st.metric("Categoria", detail.product.category or "Sem categoria")
with metadata_columns[2]:
    st.metric("Subcategoria", detail.product.subcategory or "n/a")
with metadata_columns[3]:
    st.metric("Classificação", _format_classification(detail.score.classification))

score_columns = st.columns(4)
with score_columns[0]:
    st.metric("Score de Oportunidade", _format_score(detail.score.final_score))
with score_columns[1]:
    st.metric("Risco de Saturação", detail.score.saturation_risk)
with score_columns[2]:
    st.metric("Penalidade de Saturação", _format_number(detail.score.saturation_penalty))
with score_columns[3]:
    st.metric("Estimativa de Receita", _format_currency(detail.score.revenue_estimate))

subscore_columns = st.columns(3)
with subscore_columns[0]:
    st.metric("Score de Tendência", _format_score(detail.score.trend_score))
with subscore_columns[1]:
    st.metric("Score Viral", _format_score(detail.score.viral_potential_score))
with subscore_columns[2]:
    st.metric("Score de Acessibilidade", _format_score(detail.score.creator_accessibility_score))

st.subheader("Resumo do Produto")
if explanation.summary is None:
    st.info("Nenhum resumo disponível para este produto.")
else:
    st.write(explanation.summary)

signal_columns = st.columns(2)
with signal_columns[0]:
    st.write("**Sinais Positivos**")
    _render_bullet_list(
        explanation.top_positive_signals or explanation.strengths,
        empty_message="Nenhum sinal positivo registrado.",
    )
with signal_columns[1]:
    st.write("**Sinais Negativos**")
    _render_bullet_list(
        explanation.top_negative_signals or explanation.weaknesses,
        empty_message="Nenhum sinal negativo registrado.",
    )

st.write("**Evidências**")
_render_bullet_list(explanation.evidence, empty_message="Nenhuma evidência registrada.")

if detail.score.risk_flags:
    st.write("**Alertas de Risco**")
    _render_bullet_list(detail.score.risk_flags, empty_message="Sem alertas de risco.")

st.divider()
st.subheader("Último Snapshot")
if detail.latest_snapshot is None:
    st.info("Nenhum snapshot disponível para este produto.")
else:
    snapshot_columns = st.columns(3)
    with snapshot_columns[0]:
        st.metric("Preço", _format_currency(detail.latest_snapshot.price))
    with snapshot_columns[1]:
        st.metric("Estimativa de Pedidos", detail.latest_snapshot.orders_estimate or 0)
    with snapshot_columns[2]:
        st.metric(
            "Taxa de Comissão",
            "n/a"
            if detail.latest_snapshot.commission_rate is None
            else f"{detail.latest_snapshot.commission_rate:.2f}%",
        )

    snapshot_metadata_columns = st.columns(3)
    with snapshot_metadata_columns[0]:
        st.metric(
            "Avaliação",
            "n/a"
            if detail.latest_snapshot.rating is None
            else f"{detail.latest_snapshot.rating:.2f}",
        )
    with snapshot_metadata_columns[1]:
        st.metric("Capturado em", detail.latest_snapshot.captured_at)
    with snapshot_metadata_columns[2]:
        st.metric("Fonte", detail.latest_snapshot.source_name)

    if detail.latest_snapshot.source_record_id is not None:
        st.caption(f"ID do registro fonte: {detail.latest_snapshot.source_record_id}")

st.divider()
st.subheader("Raciocínio dos Agentes")

trend_tab, viral_tab, creator_tab = st.tabs(
    [
        "Agente de Tendência",
        "Agente de Potencial Viral",
        "Agente de Acessibilidade",
    ]
)

with trend_tab:
    _render_agent_reasoning(
        agent_reasoning["trend"],
        empty_message="Nenhum raciocínio de tendência disponível.",
    )
with viral_tab:
    _render_agent_reasoning(
        agent_reasoning["viral_potential"],
        empty_message="Nenhum raciocínio de potencial viral disponível.",
    )
with creator_tab:
    _render_agent_reasoning(
        agent_reasoning["creator_accessibility"],
        empty_message="Nenhum raciocínio de acessibilidade disponível.",
    )
