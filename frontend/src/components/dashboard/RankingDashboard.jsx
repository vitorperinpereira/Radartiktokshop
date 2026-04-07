import { useEffect, useState } from "react";
import { FilterBar } from "./FilterBar";
import { SortControls } from "./SortControls";
import { ProductRow } from "./ProductRow";
import { ClassificationBadge } from "./ClassificationBadge";
import { WeekBadge } from "./WeekBadge";
import { fetchRankingMeta } from "../../api/ranking";
import { useFilters } from "../../hooks/useFilters";
import { useRanking } from "../../hooks/useRanking";
import { formatCurrency } from "../../utils/formatters";
import { getAccelerationIcon } from "../../utils/scoreColors";
import { Link } from "react-router-dom";

function HeroCard({ entry }) {
  if (!entry) return null;
  return (
    <section className="relative rounded-xl p-[2px] bg-gradient-to-r from-primary to-accent shadow-soft hover-lift">
      <div className="bg-surface dark:bg-surface-dark rounded-[14px] p-1 flex flex-col md:flex-row h-full">
        {/* Image Side */}
        <div className="relative w-full md:w-2/5 aspect-[4/3] md:aspect-auto md:min-h-[320px] rounded-lg overflow-hidden m-2 md:m-3">
          <div
            className="absolute inset-0 bg-cover bg-center"
            style={{
              backgroundImage: `url("https://wsrv.nl/?url=${encodeURIComponent(entry.image_url)}&default=${encodeURIComponent("https://placehold.co/600x400")}")`,
            }}
          ></div>
          <div className="absolute top-3 left-3 bg-text-main dark:bg-surface-dark text-white text-xs font-bold px-3 py-1.5 rounded-full flex items-center gap-1 shadow-md">
            <span
              className="material-symbols-outlined"
              style={{ fontSize: "14px", color: "var(--color-warning)" }}
            >
              trophy
            </span>
            TOP 1 DA SEMANA
          </div>
        </div>

        {/* Content Side */}
        <div className="flex-1 p-5 md:p-8 flex flex-col justify-between">
          <div className="space-y-4">
            <div className="flex items-start justify-between gap-4">
              <div>
                <span className="inline-block px-2.5 py-1 bg-outline/30 dark:bg-surface-dark text-muted text-xs font-semibold rounded-md mb-3">
                  {entry.category || "Sem Categoria"}
                </span>
                <h3 className="text-2xl md:text-3xl font-bold text-text-main dark:text-white leading-tight mb-2">
                  {entry.name}
                </h3>
                <p className="text-muted text-sm md:text-base line-clamp-2">
                  Destacando-se esta semana com score impressionante e excelente
                  conversão.
                </p>
              </div>

              {/* Large Score Gauge */}
              <div className="flex-shrink-0 flex flex-col items-center">
                <div className="relative w-20 h-20 md:w-24 md:h-24">
                  <svg
                    className="w-full h-full transform -rotate-90"
                    viewBox="0 0 100 100"
                  >
                    <circle
                      cx="50"
                      cy="50"
                      fill="none"
                      r="40"
                      stroke-outline
                      strokeWidth="8"
                    ></circle>
                    <circle
                      className="gauge-circle"
                      cx="50"
                      cy="50"
                      fill="none"
                      r="40"
                      stroke-success
                      strokeDasharray={`${(entry.final_score / 100) * 251} 251`}
                      strokeLinecap="round"
                      strokeWidth="8"
                    ></circle>
                  </svg>
                  <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className="text-2xl md:text-3xl font-black text-text-main dark:text-white">
                      {Number(entry.final_score).toFixed(0)}
                    </span>
                  </div>
                </div>
                <span className="text-[10px] md:text-xs font-bold text-success mt-1 uppercase tracking-wider">
                  Oportunidade
                </span>
              </div>
            </div>

            <div className="flex flex-wrap gap-2 mt-4">
              <span className="flex items-center gap-1 text-xs font-medium bg-accent/10 text-accent px-2.5 py-1 rounded-md">
                <span
                  className="material-symbols-outlined"
                  style={{ fontSize: "14px" }}
                >
                  trending_up
                </span>
                {getAccelerationIcon(entry.acceleration_bonus)}{" "}
                {entry.acceleration_bonus > 0 ? "Acelerando" : "Estável"}
              </span>
              <span className="flex items-center gap-1 text-xs font-medium bg-green-50 dark:bg-green-900/30 text-green-700 dark:text-green-400 px-2.5 py-1 rounded-md">
                <span
                  className="material-symbols-outlined"
                  style={{ fontSize: "14px" }}
                >
                  speed
                </span>{" "}
                Alta Métrica
              </span>
              {entry.label && (
                <ClassificationBadge classification={entry.label} />
              )}
            </div>
          </div>

          <div className="mt-8 flex items-center justify-between">
            <div className="text-sm font-medium">
              <span className="text-muted">Comissão por Venda:</span>
              <span className="text-success font-bold text-lg md:text-xl ml-1">
                {formatCurrency(entry.commission_per_sale || 0)}
              </span>
            </div>
            <Link
              to={`/product/${entry.product_id}`}
              className="bg-primary hover:bg-primary/90 text-white font-semibold py-3 px-6 rounded-lg transition-colors flex items-center gap-2 shadow-md hover:shadow-lg"
            >
              Analisar Produto
              <span
                className="material-symbols-outlined"
                style={{ fontSize: "18px" }}
              >
                arrow_forward
              </span>
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}

export function RankingDashboard() {
  const [meta, setMeta] = useState(null);

  const {
    filters,
    sortBy,
    order,
    page,
    setFilters,
    setSortBy,
    setOrder,
    setPage,
  } = useFilters();

  const { entries, total, loading, error } = useRanking(
    filters,
    sortBy,
    order,
    page,
  );

  useEffect(() => {
    fetchRankingMeta().then(setMeta).catch(console.error);
  }, []);

  const pageSize = 20;
  const totalPages = Math.ceil(total / pageSize);

  const topEntry = page === 1 && entries.length > 0 ? entries[0] : null;
  const listEntries = page === 1 ? entries.slice(1) : entries;

  return (
    <div className="p-4 md:p-8 lg:p-10 max-w-5xl mx-auto space-y-8 w-full">
      {/* Page Header */}
      <div className="space-y-2">
        <h2 className="text-3xl md:text-4xl font-black text-text-main dark:text-white tracking-tight">
          Radar Semanal
        </h2>
        <p className="text-muted text-base md:text-lg flex justify-between items-center">
          <span>Descubra os produtos com maior potencial hoje.</span>
          {meta && (
            <span className="text-sm flex items-center gap-2">
              <WeekBadge weekLabel={meta.week_label} />
              <span>({meta.total_products} analisados)</span>
            </span>
          )}
        </p>
      </div>

      {error ? (
        <div className="p-6 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-lg border border-red-200 dark:border-red-800">
          <p className="font-bold">
            Erro ao carregar ranking. Recarregue a pagina ou tente novamente em
            instantes.
          </p>
          <p className="text-sm mt-2">{error}</p>
        </div>
      ) : loading ? (
        <div className="space-y-4">
          {[...Array(5)].map((_, i) => (
            <div
              key={i}
              className="h-24 bg-surface dark:bg-surface-dark rounded-lg border border-outline dark:border-outline/20 animate-pulse"
            />
          ))}
        </div>
      ) : entries.length === 0 ? (
        <div className="p-12 text-center text-muted bg-surface dark:bg-surface-dark rounded-lg border border-outline dark:border-outline/20">
          Nenhum produto encontrado com esses filtros. Ajuste categoria, label
          ou score minimo e tente de novo.
        </div>
      ) : (
        <>
          {/* Top 1 Produto */}
          {topEntry && <HeroCard entry={topEntry} />}

          {/* Filters & Sort */}
          <div className="pt-2">
            <FilterBar
              categories={meta?.available_categories || []}
              labels={meta?.available_labels || []}
              filters={filters}
              onFilterChange={setFilters}
              onReset={() => {
                setFilters({
                  category: "",
                  label: "",
                  min_score: 0,
                  classification: "",
                });
              }}
            />
            <SortControls
              sortBy={sortBy}
              order={order}
              onSortChange={(field, o) => {
                setSortBy(field);
                setOrder(o);
              }}
            />
          </div>

          {/* Product Feed List */}
          <div className="space-y-3">
            {listEntries.map((entry) => (
              <ProductRow key={entry.product_id} entry={entry} />
            ))}
          </div>

          {/* Pagination */}
          {total > pageSize && (
            <div className="py-8 flex items-center gap-4 justify-center">
              <button
                disabled={page === 1}
                onClick={() => setPage(page - 1)}
                className="flex items-center gap-2 px-4 py-2 rounded-lg bg-surface dark:bg-surface-dark text-text-main dark:text-white shadow-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-outline/30 dark:hover:bg-surface-dark/80 transition-colors"
              >
                <span className="material-symbols-outlined">arrow_back</span>
                Anterior
              </button>

              <span className="text-muted text-sm font-medium">
                Página{" "}
                <strong className="text-text-main dark:text-white">
                  {page}
                </strong>{" "}
                de {totalPages}
              </span>

              <button
                disabled={page >= totalPages}
                onClick={() => setPage(page + 1)}
                className="flex items-center gap-2 px-4 py-2 rounded-lg bg-surface dark:bg-surface-dark text-text-main dark:text-white shadow-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-outline/30 dark:hover:bg-surface-dark/80 transition-colors"
              >
                Próxima
                <span className="material-symbols-outlined">arrow_forward</span>
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
