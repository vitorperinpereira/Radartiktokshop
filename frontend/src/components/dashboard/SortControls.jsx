export function SortControls({ sortBy, order, onSortChange }) {
  const toggleSort = (field) => {
    if (sortBy === field) {
      onSortChange(field, order === "desc" ? "asc" : "desc");
    } else {
      onSortChange(field, "desc");
    }
  };

  const getArrow = (field) =>
    sortBy === field ? (order === "desc" ? " \u2193" : " \u2191") : "";

  const getStyle = (field) =>
    `flex items-center gap-1 px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
      sortBy === field
        ? "bg-primary/10 text-primary border-transparent"
        : "bg-surface dark:bg-surface-dark border border-outline dark:border-outline/20 text-text-main dark:text-muted hover:border-primary"
    }`;

  return (
    <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-hide w-full shadow-sm mb-6">
      <span className="text-sm font-medium text-text-muted mr-2">
        Ordenar por:
      </span>
      <button
        className={getStyle("final_score")}
        onClick={() => toggleSort("final_score")}
      >
        Score{getArrow("final_score")}
      </button>
      <button
        className={getStyle("estimated_weekly_commission")}
        onClick={() => toggleSort("estimated_weekly_commission")}
      >
        Comissao{getArrow("estimated_weekly_commission")}
      </button>
      <button
        className={getStyle("trend_score")}
        onClick={() => toggleSort("trend_score")}
      >
        Tendencia{getArrow("trend_score")}
      </button>
      <button
        className={getStyle("viral_score")}
        onClick={() => toggleSort("viral_score")}
      >
        Viral{getArrow("viral_score")}
      </button>
      <button
        className={getStyle("acceleration_bonus")}
        onClick={() => toggleSort("acceleration_bonus")}
      >
        Aceleracao{getArrow("acceleration_bonus")}
      </button>
      <button
        className={getStyle("days_since_detected")}
        onClick={() => toggleSort("days_since_detected")}
      >
        Descoberta{getArrow("days_since_detected")}
      </button>
    </div>
  );
}
