const CLASSIFICATIONS = [
  { value: "EXPLOSIVE", label: "Explosivo" },
  { value: "HIGH", label: "Alto Potencial" },
  { value: "WORTH_TEST", label: "Vale Testar" },
  { value: "NICHE", label: "Nicho" },
  { value: "LOW", label: "Baixo" },
];

export function FilterBar({
  categories = [],
  labels = [],
  filters,
  onFilterChange,
  onReset,
}) {
  const hasActiveFilters =
    filters.category ||
    filters.label ||
    filters.min_score > 0 ||
    filters.classification;

  return (
    <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-hide w-full mb-4">
      <select
        value={filters.category || ""}
        onChange={(e) => onFilterChange({ category: e.target.value })}
        className="flex items-center gap-2 px-4 py-2 rounded-full bg-surface dark:bg-surface-dark text-text-main dark:text-muted border border-outline dark:border-outline/20 hover:border-primary hover:text-primary text-sm font-medium whitespace-nowrap transition-colors outline-none cursor-pointer shadow-sm"
      >
        <option value="">Todas as categorias</option>
        {categories.map((c) => (
          <option key={c} value={c}>
            {c}
          </option>
        ))}
      </select>

      <select
        value={filters.classification || ""}
        onChange={(e) => onFilterChange({ classification: e.target.value })}
        className="flex items-center gap-2 px-4 py-2 rounded-full bg-surface dark:bg-surface-dark text-text-main dark:text-muted border border-outline dark:border-outline/20 hover:border-primary hover:text-primary text-sm font-medium whitespace-nowrap transition-colors outline-none cursor-pointer shadow-sm"
      >
        <option value="">Classificacao</option>
        {CLASSIFICATIONS.map((c) => (
          <option key={c.value} value={c.value}>
            {c.label}
          </option>
        ))}
      </select>

      <button
        onClick={() => onFilterChange({ label: "" })}
        className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-colors shadow-sm cursor-pointer ${
          !filters.label
            ? "bg-text-main dark:bg-outline/30 text-white dark:text-text-main border-transparent"
            : "bg-surface dark:bg-surface-dark text-text-main dark:text-muted border border-outline dark:border-outline/20 hover:border-primary hover:text-primary"
        }`}
      >
        Todos
      </button>

      {labels.map((lbl) => (
        <button
          key={lbl}
          onClick={() =>
            onFilterChange({ label: filters.label === lbl ? "" : lbl })
          }
          className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-colors shadow-sm cursor-pointer ${
            filters.label === lbl
              ? "bg-text-main dark:bg-outline/30 text-white dark:text-text-main border-transparent"
              : "bg-surface dark:bg-surface-dark text-text-main dark:text-muted border border-outline dark:border-outline/20 hover:border-primary hover:text-primary"
          }`}
        >
          {lbl === "EXPLOSIVE" && (
            <span
              className="material-symbols-outlined shrink-0"
              style={{ fontSize: "16px" }}
            >
              local_fire_department
            </span>
          )}
          {lbl === "HIGH" && (
            <span
              className="material-symbols-outlined shrink-0"
              style={{ fontSize: "16px" }}
            >
              trending_up
            </span>
          )}
          {lbl === "NEW" && (
            <span
              className="material-symbols-outlined shrink-0"
              style={{ fontSize: "16px" }}
            >
              new_releases
            </span>
          )}
          {lbl}
        </button>
      ))}

      <div className="flex flex-1 min-w-4" />

      <div className="flex items-center gap-2 bg-surface dark:bg-surface-dark px-4 py-2 rounded-full border border-outline dark:border-outline/20 shadow-sm whitespace-nowrap hidden md:flex shrink-0">
        <span className="text-sm font-medium text-text-muted">
          Score min:{" "}
          <strong className="text-text-main dark:text-white">
            {filters.min_score || 0}
          </strong>
        </span>
        <input
          type="range"
          min="0"
          max="100"
          step="5"
          value={filters.min_score || 0}
          onChange={(e) =>
            onFilterChange({ min_score: Number(e.target.value) })
          }
          className="w-24 accent-primary cursor-pointer"
        />
      </div>

      {hasActiveFilters && onReset && (
        <button
          onClick={onReset}
          className="flex items-center gap-1 px-3 py-2 rounded-full text-sm font-medium text-danger hover:bg-danger/10 transition-colors whitespace-nowrap"
        >
          <span
            className="material-symbols-outlined"
            style={{ fontSize: "16px" }}
          >
            filter_alt_off
          </span>
          Limpar
        </button>
      )}
    </div>
  );
}
