import { useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { useContentAngles } from "../hooks/useContentAngles";

const ANGLE_LABELS = {
  momentum_hook: "Gancho de Momentum",
  social_proof: "Prova Social",
  problem_solution: "Problema-Solucao",
  curiosity_gap: "Lacuna de Curiosidade",
  transformation: "Transformacao",
  urgency: "Urgencia",
  comparison: "Comparacao",
  storytelling: "Storytelling",
  unboxing: "Unboxing",
  tutorial: "Tutorial",
};

function getAngleLabel(angleType) {
  return (
    ANGLE_LABELS[angleType] ||
    angleType.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())
  );
}

function getAngleIcon(angleType) {
  switch (angleType) {
    case "momentum_hook":
      return "rocket_launch";
    case "social_proof":
      return "group";
    case "problem_solution":
      return "lightbulb";
    case "curiosity_gap":
      return "help";
    case "transformation":
      return "auto_fix_high";
    case "urgency":
      return "timer";
    case "comparison":
      return "compare";
    case "storytelling":
      return "menu_book";
    case "unboxing":
      return "package_2";
    case "tutorial":
      return "school";
    default:
      return "capture";
  }
}

export function ContentIdeas() {
  const [searchParams] = useSearchParams();
  const productId = searchParams.get("product");
  const { angles, loading, error } = useContentAngles(productId);
  const [copiedIndex, setCopiedIndex] = useState(null);

  const copyToClipboard = (text, index) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  return (
    <div className="flex-1 w-full max-w-[800px] mx-auto px-4 py-8 md:p-10 flex flex-col">
      {/* Breadcrumbs & Header */}
      <div className="mb-8">
        <div className="flex items-center text-sm text-muted mb-4 space-x-2">
          <Link to="/" className="hover:text-primary transition-colors">
            Radar
          </Link>
          <span>/</span>
          {productId && (
            <>
              <Link
                to={`/product/${productId}`}
                className="hover:text-primary transition-colors"
              >
                Produto
              </Link>
              <span>/</span>
            </>
          )}
          <span className="text-text-main dark:text-white font-medium">
            Laboratorio de Angulos
          </span>
        </div>
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div>
            <h2 className="text-3xl md:text-4xl font-bold text-text-main dark:text-white tracking-tight">
              Laboratorio de Angulos
            </h2>
            <p className="text-muted mt-2">
              Estrategias de conteudo geradas por IA para o seu produto.
            </p>
          </div>
        </div>
      </div>

      {/* Content Area */}
      <div className="bg-surface dark:bg-surface-dark rounded-[24px] shadow-soft p-6 md:p-10 border border-outline dark:border-outline/20 relative flex-1">
        <div className="absolute top-0 left-8 w-12 h-4 bg-primary/20 rounded-b-lg"></div>

        {!productId ? (
          <div className="flex flex-col items-center justify-center h-64 text-muted">
            <span className="material-symbols-outlined text-4xl mb-3">
              search_off
            </span>
            <p className="font-medium mb-2">Nenhum produto selecionado</p>
            <p className="text-sm mb-4">
              Selecione um produto no Radar para ver angulos de conteudo.
            </p>
            <Link
              to="/"
              className="inline-flex items-center gap-2 px-4 py-2 bg-primary/10 text-primary rounded-lg font-medium text-sm hover:bg-primary/20 transition-colors"
            >
              <span
                className="material-symbols-outlined"
                style={{ fontSize: "18px" }}
              >
                radar
              </span>
              Ir para o Radar
            </Link>
          </div>
        ) : loading ? (
          <div className="flex flex-col items-center justify-center h-64 text-muted">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-primary mb-4"></div>
            <p>Carregando angulos de conteudo...</p>
          </div>
        ) : error ? (
          <div className="flex flex-col items-center justify-center h-64 text-danger">
            <span className="material-symbols-outlined text-3xl mb-2">
              error
            </span>
            <p className="text-sm">
              {error}. Tente novamente ou volte ao Radar.
            </p>
          </div>
        ) : angles.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-64 text-muted">
            <span className="material-symbols-outlined text-4xl mb-3">
              lightbulb
            </span>
            <p className="font-medium mb-2">Nenhum angulo gerado ainda</p>
            <p className="text-sm">
              Os angulos de conteudo serao gerados na proxima execucao do
              pipeline.
            </p>
          </div>
        ) : (
          <div className="space-y-8 mt-4">
            {angles.map((angle, index) => (
              <section key={index} className="relative group">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <span className="material-symbols-outlined text-primary text-xl">
                      {getAngleIcon(angle.angle_type)}
                    </span>
                    <h3 className="text-lg font-semibold text-text-main dark:text-white">
                      {getAngleLabel(angle.angle_type)}
                    </h3>
                    <span className="text-xs text-text-muted bg-outline/30 dark:bg-surface-dark px-2 py-0.5 rounded">
                      {angle.week_start}
                    </span>
                  </div>
                  <button
                    onClick={() => copyToClipboard(angle.hook_text, index)}
                    className="w-8 h-8 flex items-center justify-center rounded-lg bg-outline/30 dark:bg-surface-dark text-muted hover:text-primary transition-colors"
                  >
                    <span className="material-symbols-outlined text-[18px]">
                      {copiedIndex === index ? "check" : "content_copy"}
                    </span>
                  </button>
                </div>
                <div className="bg-outline/30 dark:bg-surface-dark/50 p-6 rounded-xl border border-outline dark:border-outline/20">
                  <p className="text-xl md:text-2xl font-bold text-text-main dark:text-white leading-tight italic">
                    "{angle.hook_text}"
                  </p>
                </div>
                {angle.supporting_rationale && (
                  <div className="mt-3 pl-4 border-l-2 border-primary/30">
                    <p className="text-sm text-text-muted leading-relaxed">
                      {angle.supporting_rationale}
                    </p>
                  </div>
                )}
                {index < angles.length - 1 && (
                  <hr className="border-outline dark:border-outline/20 mt-8" />
                )}
              </section>
            ))}
          </div>
        )}
      </div>

      {/* Copy Toast */}
      {copiedIndex !== null && (
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 bg-surface-dark text-white px-4 py-3 rounded-lg shadow-hover flex items-center gap-3 z-50">
          <span className="material-symbols-outlined text-primary">
            check_circle
          </span>
          <span className="font-medium text-sm">
            Copiado para a area de transferencia!
          </span>
        </div>
      )}
    </div>
  );
}
