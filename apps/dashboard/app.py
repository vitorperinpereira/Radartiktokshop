"""Read-only Streamlit entrypoint for the Creator Product Radar dashboard."""

from __future__ import annotations

import streamlit as st

from apps.dashboard.read_adapter import load_rankings

st.set_page_config(page_title="Radar de Produtos", page_icon="📡", layout="wide")

st.title("📡 Radar de Produtos para Criadores")
st.markdown(
    "Painel de análise semanal de produtos do TikTok Shop. "
    "Execute o fluxo via CLI primeiro, depois revise o ranking aqui."
)

ranking_result = load_rankings()
if ranking_result.error is not None:
    st.error(ranking_result.error)
    st.stop()

ranking = ranking_result.data
if ranking is None or ranking.count == 0:
    st.info(
        "Nenhum ranking semanal disponível ainda. "
        "Execute `db-upgrade`, `ingest-mock` e `weekly-run` via CLI primeiro."
    )
else:
    top_item = ranking.items[0]
    metric_columns = st.columns(3)
    with metric_columns[0]:
        st.metric("Semana analisada", ranking.week_start or "n/a")
    with metric_columns[1]:
        st.metric("Produtos pontuados", ranking.count)
    with metric_columns[2]:
        st.metric(
            "Maior Score de Oportunidade",
            "n/a" if top_item.final_score is None else f"{top_item.final_score:.1f}",
        )

    st.success("Ranking semanal carregado com sucesso.")
    st.caption(
        "Use o menu lateral do Streamlit para acessar Radar Semanal, Detalhes do Produto e "
        "Histórico de Pipeline."
    )

st.divider()
st.subheader("Fluxo de Operação")
st.markdown(
    "1. Execute `db-upgrade`, `ingest-mock` e `weekly-run` via CLI.\n"
    "2. Revise o ranking e as páginas de detalhes.\n"
    "3. Execute `export-report` quando o resultado semanal estiver pronto para revisão."
)
