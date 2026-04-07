"""Pipeline History page for the dashboard."""

from __future__ import annotations

import pandas as pd  # type: ignore[import-untyped]
import streamlit as st

from apps.dashboard.read_adapter import load_pipeline_history

st.set_page_config(page_title="Histórico de Pipeline", page_icon="📊", layout="wide")

st.title("📊 Histórico de Execuções do Pipeline")
st.markdown("Monitore as execuções do pipeline através do painel de análise.")

history_result = load_pipeline_history()
if history_result.error is not None:
    st.error(history_result.error)
    st.stop()

history = history_result.data
if history is None or history.count == 0:
    st.info("Nenhum histórico de pipeline disponível ainda. Execute o fluxo semanal primeiro.")
    st.stop()

latest_run = history.items[0]
summary_columns = st.columns(3)
with summary_columns[0]:
    st.metric("Total de Execuções", history.count)
with summary_columns[1]:
    st.metric("Último Status", latest_run.status)
with summary_columns[2]:
    st.metric("Produtos Pontuados (Último)", latest_run.scored_products)

st.success("Histórico de pipeline carregado com sucesso.")
st.divider()

history_df = pd.DataFrame([item.model_dump() for item in history.items])
st.subheader("Execuções Recentes")
st.dataframe(history_df, hide_index=True, use_container_width=True)

st.divider()
st.subheader("Detalhes da Última Execução")
st.code(
    "\n".join(
        [
            f"Run ID: {latest_run.run_id}",
            f"Semana: {latest_run.week_start}",
            f"Status: {latest_run.status}",
            f"Produtos Pontuados: {latest_run.scored_products}",
            f"Score Máximo: {latest_run.top_final_score}",
            f"Classificação Topo: {latest_run.top_classification}",
            f"Relatórios Gerados: {latest_run.report_count}",
        ]
    ),
    language="text",
)
