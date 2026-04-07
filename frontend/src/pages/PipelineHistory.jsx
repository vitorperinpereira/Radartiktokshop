import { useState } from "react";
import { Link } from "react-router-dom";
import { usePipelineHistory } from "../hooks/usePipelineHistory";
import { formatDate } from "../utils/formatters";

const STATUS_STYLES = {
  completed: "bg-success/10 text-success border-success/20",
  running: "bg-warning/10 text-warning border-warning/20",
  failed: "bg-danger/10 text-danger border-danger/20",
};

const STATUS_ICONS = {
  completed: "check_circle",
  running: "sync",
  failed: "error",
};

function formatDuration(seconds) {
  if (seconds == null) return "-";
  if (seconds < 60) return `${seconds}s`;
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}m ${s}s`;
}

export function PipelineHistory() {
  const { runs, loading, error } = usePipelineHistory(50);
  const [expandedId, setExpandedId] = useState(null);

  return (
    <div className="p-4 md:p-8 lg:p-10 max-w-5xl mx-auto space-y-6 w-full">
      <div className="space-y-2">
        <div className="flex items-center text-sm text-muted mb-2 space-x-2">
          <Link to="/" className="hover:text-primary transition-colors">
            Radar
          </Link>
          <span>/</span>
          <span className="text-text-main dark:text-white font-medium">
            Historico
          </span>
        </div>
        <h2 className="text-3xl md:text-4xl font-black text-text-main dark:text-white tracking-tight">
          Historico do Pipeline
        </h2>
        <p className="text-muted">Execucoes do pipeline de analise semanal.</p>
      </div>

      {error ? (
        <div className="p-6 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-lg border border-red-200 dark:border-red-800">
          <p className="font-bold">
            Erro ao carregar historico. Recarregue a pagina ou tente novamente
            em instantes.
          </p>
          <p className="text-sm mt-2">{error}</p>
        </div>
      ) : loading ? (
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => (
            <div
              key={i}
              className="h-16 bg-surface dark:bg-surface-dark rounded-lg border border-outline dark:border-outline/20 animate-pulse"
            />
          ))}
        </div>
      ) : runs.length === 0 ? (
        <div className="p-12 text-center text-muted bg-surface dark:bg-surface-dark rounded-lg border border-outline dark:border-outline/20">
          <span className="material-symbols-outlined text-4xl mb-3 block">
            history
          </span>
          Nenhuma execução encontrada.
        </div>
      ) : (
        <div className="bg-surface dark:bg-surface-dark rounded-lg shadow-soft border border-outline dark:border-outline/20 overflow-hidden">
          {/* Header */}
          <div className="hidden md:grid grid-cols-6 gap-4 px-4 py-3 bg-outline/30 dark:bg-surface-dark text-xs font-semibold text-text-muted uppercase tracking-wide border-b border-outline dark:border-outline/20">
            <span>Semana</span>
            <span>Status</span>
            <span>Duracao</span>
            <span>Produtos</span>
            <span>Top Score</span>
            <span>Inicio</span>
          </div>

          {runs.map((run) => {
            const statusStyle =
              STATUS_STYLES[run.status] || STATUS_STYLES.failed;
            const statusIcon = STATUS_ICONS[run.status] || "help";
            const isExpanded = expandedId === run.run_id;

            return (
              <div key={run.run_id}>
                <div
                  className="grid grid-cols-2 md:grid-cols-6 gap-2 md:gap-4 px-4 py-3 border-b border-outline dark:border-outline/20 hover:bg-outline/30 dark:hover:bg-surface-dark/80/50 cursor-pointer transition-colors"
                  onClick={() => setExpandedId(isExpanded ? null : run.run_id)}
                >
                  <span className="font-semibold text-text-main dark:text-white text-sm">
                    {run.week_start}
                  </span>
                  <span>
                    <span
                      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium border ${statusStyle}`}
                    >
                      <span
                        className="material-symbols-outlined"
                        style={{ fontSize: "14px" }}
                      >
                        {statusIcon}
                      </span>
                      {run.status}
                    </span>
                  </span>
                  <span className="text-sm text-text-muted hidden md:block">
                    {formatDuration(run.duration_seconds)}
                  </span>
                  <span className="text-sm text-text-main dark:text-white hidden md:block">
                    {run.scored_products}
                  </span>
                  <span className="text-sm font-bold text-success hidden md:block">
                    {run.top_final_score != null
                      ? Number(run.top_final_score).toFixed(1)
                      : "-"}
                  </span>
                  <span className="text-sm text-text-muted hidden md:block">
                    {formatDate(run.started_at)}
                  </span>
                </div>

                {isExpanded && run.error_summary && (
                  <div className="px-4 py-3 bg-danger/5 border-b border-outline dark:border-outline/20">
                    <p className="text-sm font-medium text-danger mb-1">
                      Erro:
                    </p>
                    <pre className="text-xs text-text-muted whitespace-pre-wrap font-mono bg-outline/30 dark:bg-surface-dark p-3 rounded">
                      {run.error_summary}
                    </pre>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
