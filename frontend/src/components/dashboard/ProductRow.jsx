import { useState } from "react";
import { VideoDrawer } from "./VideoDrawer";
import { ClassificationBadge } from "./ClassificationBadge";
import { formatCurrency, formatDaysAgo } from "../../utils/formatters";
import { Link } from "react-router-dom";
import { useGarage } from "../../hooks/useGarage";

export function ProductRow({ entry }) {
  const [showVideos, setShowVideos] = useState(false);
  const { isSaved, saveProduct, removeProduct } = useGarage();

  if (!entry) return null;

  const scoreColor =
    entry.final_score >= 80
      ? "text-success"
      : entry.final_score >= 60
        ? "text-warning"
        : "text-danger";
  const scoreBadgeBg =
    entry.final_score >= 80
      ? "stroke-success"
      : entry.final_score >= 60
        ? "stroke-warning"
        : "stroke-primary";

  return (
    <div className="bg-surface dark:bg-surface-dark rounded-lg p-3 md:p-4 flex items-center gap-4 shadow-soft hover-lift group border border-transparent dark:border-outline/20 hover:border-outline dark:hover:border-outline/40">
      <div className="w-16 h-16 md:w-20 md:h-20 flex-shrink-0 rounded-md overflow-hidden relative bg-outline/30 dark:bg-surface-dark">
        <img
          alt={entry.name}
          className="w-full h-full object-cover"
          src={
            entry.image_url
              ? `https://wsrv.nl/?url=${encodeURIComponent(entry.image_url)}&default=${encodeURIComponent("https://placehold.co/100x100")}`
              : "https://placehold.co/100x100"
          }
        />
      </div>

      <div className="flex-1 min-w-0">
        <p className="text-xs font-semibold text-muted mb-1 flex items-center gap-2">
          <span className="font-bold text-text-main dark:text-muted">
            #{entry.rank}
          </span>
          {entry.category || "Sem Categoria"}
          {entry.label && <ClassificationBadge classification={entry.label} />}
        </p>
        <h4 className="text-base md:text-lg font-bold text-text-main dark:text-white truncate group-hover:text-primary transition-colors">
          {entry.name}
        </h4>
        <div className="flex flex-wrap items-center gap-3 mt-1 text-sm">
          <span className="text-muted">
            Comissão:{" "}
            <strong className="text-text-main dark:text-white">
              {formatCurrency(entry.commission_per_sale || 0)}
            </strong>
          </span>
          <span className="text-muted text-xs hidden sm:inline-block">
            Detectado {formatDaysAgo(entry.days_since_detected)}
          </span>
        </div>
      </div>

      <div className="flex-shrink-0 flex items-center gap-4 md:gap-6">
        <div className="text-center hidden sm:block">
          <span className={`block text-xl font-black ${scoreColor}`}>
            {Number(entry.final_score).toFixed(0)}
          </span>
          <span className="text-[10px] uppercase font-bold text-muted">
            Score
          </span>
        </div>

        {/* Small Gauge for Mobile */}
        <div className="sm:hidden relative w-10 h-10">
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
              strokeWidth="12"
            ></circle>
            <circle
              cx="50"
              cy="50"
              fill="none"
              r="40"
              className={scoreBadgeBg}
              strokeDasharray={`${(entry.final_score / 100) * 251} 251`}
              strokeWidth="12"
              strokeLinecap="round"
            ></circle>
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="text-xs font-bold dark:text-white">
              {Number(entry.final_score).toFixed(0)}
            </span>
          </div>
        </div>

        <div className="flex gap-2">
          <button
            onClick={(e) => {
              e.preventDefault();
              isSaved(entry.product_id)
                ? removeProduct(entry.product_id)
                : saveProduct(entry);
            }}
            className={`flex items-center justify-center w-9 h-9 border rounded-md transition-colors ${
              isSaved(entry.product_id)
                ? "bg-surface dark:bg-surface-dark border-outline dark:border-outline/20 text-text-main dark:text-white hover:bg-red-50 dark:hover:bg-red-900/20 hover:text-danger hover:border-danger"
                : "bg-surface dark:bg-surface-dark border-outline dark:border-outline/20 text-text-muted hover:border-primary hover:text-primary"
            }`}
            title={
              isSaved(entry.product_id)
                ? "Remover da Garagem"
                : "Salvar na Garagem"
            }
          >
            <span
              className="material-symbols-outlined"
              style={{ fontSize: "18px" }}
            >
              {isSaved(entry.product_id) ? "garage" : "add_box"}
            </span>
          </button>

          <button
            onClick={() => setShowVideos(!showVideos)}
            className="flex items-center gap-1 bg-surface dark:bg-surface-dark border border-outline dark:border-outline/20 hover:border-primary text-text-main dark:text-white font-semibold py-2 px-3 rounded-md transition-colors text-sm"
          >
            <span
              className="material-symbols-outlined"
              style={{ fontSize: "18px" }}
            >
              play_circle
            </span>
            <span className="hidden md:inline">Vídeos</span>
          </button>

          <Link
            to={`/product/${entry.product_id}`}
            className="hidden md:flex bg-primary/10 text-primary hover:bg-primary hover:text-white font-semibold py-2 px-4 rounded-md transition-colors items-center gap-1 text-sm"
          >
            Analisar
          </Link>
          <Link
            to={`/product/${entry.product_id}`}
            className="md:hidden text-primary p-2"
          >
            <span className="material-symbols-outlined">chevron_right</span>
          </Link>
        </div>
      </div>

      <VideoDrawer
        productId={entry.product_id}
        productName={entry.name}
        isOpen={showVideos}
        onClose={() => setShowVideos(false)}
      />
    </div>
  );
}
