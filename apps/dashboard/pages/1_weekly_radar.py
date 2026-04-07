"""Weekly Radar page for the dashboard."""

from __future__ import annotations

import streamlit as st

from apps.dashboard.read_adapter import (
    available_categories,
    filter_ranking_items,
    load_rankings,
    product_option_label,
    ranking_items_to_dataframe,
)

st.set_page_config(page_title="Radar Semanal", page_icon="🎯", layout="wide")


def _average_score(items_count: int, *, score_total: float) -> int:
    if items_count == 0:
        return 0
    return int(round(score_total / items_count))


st.title("🎯 Radar de Oportunidades Semanal")
st.markdown("Produtos do TikTok Shop ranqueados pelo Score de Oportunidade para Criadores.")

ranking_result = load_rankings()
if ranking_result.error is not None:
    st.error(ranking_result.error)
    st.stop()

ranking = ranking_result.data
if ranking is None or ranking.count == 0:
    st.info("Nenhum ranking semanal disponível ainda. Execute o pipeline semanal primeiro.")
    st.stop()

st.caption(f"Semana analisada: {ranking.week_start}")

st.sidebar.header("Filtros")
selected_categories = st.sidebar.multiselect(
    "Categoria",
    options=available_categories(ranking.items),
    default=[],
)
hide_high_saturation = st.sidebar.checkbox("Ocultar Alta Saturação", value=False)

filtered_items = filter_ranking_items(
    ranking.items,
    categories=selected_categories,
    hide_high_saturation=hide_high_saturation,
)
score_total = sum(item.final_score or 0 for item in filtered_items)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total de Produtos Pontuados", ranking.count)
with col2:
    st.metric("Produtos Exibidos", len(filtered_items))
with col3:
    st.metric(
        "Score Médio (Exibidos)",
        _average_score(len(filtered_items), score_total=score_total),
    )

st.divider()

if not filtered_items:
    st.info("Nenhum produto corresponde aos filtros atuais para a semana analisada.")
else:
    filtered_df = ranking_items_to_dataframe(filtered_items)
    st.dataframe(
        filtered_df,
        column_config={
            "Score de Oportunidade": st.column_config.ProgressColumn(
                "Score de Oportunidade",
                help="Score final (0-100)",
                format="%.1f",
                min_value=0,
                max_value=100,
            ),
            "Estimativa de Receita": st.column_config.NumberColumn(
                "Estimativa de Receita",
                help="Proxy de monetização determinístico.",
                format="R$ %.2f",
            ),
            "Penalidade de Saturação": st.column_config.NumberColumn(
                "Penalidade de Saturação",
                help="Penalidade aplicada durante a agregação do score.",
                format="%.2f",
            ),
            "Risco de Saturação": st.column_config.TextColumn(
                "Risco de Saturação",
                help="Baixo, Médio ou Alto com base na penalidade de saturação.",
            ),
        },
        hide_index=True,
        use_container_width=True,
    )

    st.caption(
        "Selecione um produto abaixo para abrir os Detalhes do Produto."
    )
    product_ids = [item.product_id for item in filtered_items]
    selected_product_id = st.selectbox(
        "Abrir Detalhes do Produto:",
        options=product_ids,
        format_func=lambda product_id: product_option_label(
            next(item for item in filtered_items if item.product_id == product_id)
        ),
    )
    st.session_state["selected_product_id"] = selected_product_id
    st.session_state["selected_week_start"] = ranking.week_start

    if st.button("Abrir Detalhes do Produto", type="primary"):
        st.switch_page("pages/2_product_drilldown.py")
