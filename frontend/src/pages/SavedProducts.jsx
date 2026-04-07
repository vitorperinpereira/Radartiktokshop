import { useState } from "react";
import { Link } from "react-router-dom";
import { useGarage } from "../hooks/useGarage";

export function SavedProducts() {
  const { savedProducts, updateStatus, removeProduct, loading, error } = useGarage();
  const [filterStatus, setFilterStatus] = useState("all");

  const filteredProducts =
    filterStatus === "all"
      ? savedProducts
      : savedProducts.filter((p) => p.status === filterStatus);

  if (loading) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center min-h-[50vh]">
        <div className="animate-spin text-primary mb-4">
          <span className="material-symbols-outlined text-4xl">autorenew</span>
        </div>
        <p className="text-text-muted font-medium">Buscando sua garagem...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center min-h-[50vh] p-6 text-center">
        <span className="material-symbols-outlined text-danger text-5xl mb-4">error</span>
        <h3 className="text-lg font-bold text-text-main dark:text-white mb-2">Erro ao carregar garagem</h3>
        <p className="text-text-muted">{error}</p>
      </div>
    );
  }

  const getStatusColor = (status) => {
    switch (status) {
      case "planejando":
        return "bg-outline/30 dark:bg-surface-dark text-text-main dark:text-white/90";
      case "gravando":
        return "bg-yellow-200 dark:bg-yellow-900/50 text-yellow-800 dark:text-yellow-200";
      case "publicado":
        return "bg-green-200 dark:bg-green-900/50 text-green-800 dark:text-green-200";
      default:
        return "bg-outline/30 dark:bg-surface-dark text-text-main dark:text-white/90";
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return "bg-success text-white";
    if (score >= 60) return "bg-warning text-white";
    return "bg-danger text-white";
  };

  return (
    <div className="p-6 md:p-10 max-w-7xl mx-auto w-full flex-1 animate-in fade-in duration-500">
      {/* Page Header */}
      <div className="mb-8 flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h2 className="text-3xl md:text-4xl font-bold text-text-main dark:text-white tracking-tight mb-2">
            Minha Garagem
          </h2>
          <p className="text-text-muted text-sm md:text-base">
            Acompanhe seus produtos salvos e status de criação.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="px-4 py-2 bg-surface dark:bg-surface-dark border border-outline dark:border-outline/20 rounded-lg text-sm font-medium hover:border-outline dark:hover:border-outline/40 transition-colors shadow-sm outline-none cursor-pointer text-text-main dark:text-white"
          >
            <option value="all">Todos os Status</option>
            <option value="planejando">Planejando</option>
            <option value="gravando">Gravando</option>
            <option value="publicado">Publicado</option>
          </select>
          <Link
            to="/"
            className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg text-sm font-semibold hover:bg-primary/90 transition-colors shadow-sm"
          >
            <span className="material-symbols-outlined text-[20px]">add</span>
            Ir para o Radar
          </Link>
        </div>
      </div>

      {savedProducts.length === 0 ? (
        <div className="flex flex-col items-center justify-center p-12 bg-surface dark:bg-surface-dark rounded-xl border border-outline dark:border-outline/20 text-center">
          <span className="material-symbols-outlined text-6xl text-muted dark:text-text-main mb-4">
            garage
          </span>
          <h3 className="text-xl font-bold text-text-main dark:text-white mb-2">
            Sua garagem está vazia
          </h3>
          <p className="text-text-muted max-w-md mx-auto mb-6">
            Você ainda não salvou nenhum produto. Volte ao Radar Semanal para
            explorar oportunidades e salvá-las aqui.
          </p>
          <Link
            to="/"
            className="bg-primary text-white font-medium px-6 py-2.5 rounded-lg hover:bg-primary/90 transition-colors"
          >
            Explorar Radar
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredProducts.map((product) => (
            <article
              key={product.product_id}
              className="group bg-surface dark:bg-surface-dark rounded-lg shadow-soft hover:shadow-hover border border-transparent dark:border-outline/20 hover:border-primary/20 dark:hover:border-primary/20 transition-all duration-300 flex flex-col overflow-hidden relative"
            >
              <button
                onClick={(e) => {
                  e.preventDefault();
                  removeProduct(product.product_id);
                }}
                className="absolute top-3 right-3 z-10 w-8 h-8 flex items-center justify-center bg-black/40 hover:bg-danger text-white rounded-full opacity-0 group-hover:opacity-100 transition-all"
                title="Remover da garagem"
              >
                <span className="material-symbols-outlined text-[18px]">
                  delete
                </span>
              </button>

              <Link
                to={`/product/${product.product_id}`}
                className="block relative aspect-square overflow-hidden bg-outline/30 dark:bg-surface-dark"
              >
                <img
                  alt={product.name}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                  src={product.image_url || "https://placehold.co/300x300"}
                />
                <div className="absolute top-3 left-3 flex items-center gap-1 bg-surface/90 dark:bg-surface-dark/90 backdrop-blur-sm px-2 py-1 rounded-md shadow-sm border border-outline dark:border-outline/20">
                  <span
                    className={`w-2 h-2 rounded-full ${getScoreColor(product.final_score)} ${product.final_score >= 80 ? "animate-pulse" : ""}`}
                  ></span>
                  <span className="font-bold text-sm text-text-main dark:text-white">
                    {Number(product.final_score).toFixed(0)}
                  </span>
                </div>
              </Link>

              <div className="p-4 flex flex-col flex-1">
                <div className="flex justify-between items-start mb-2">
                  <Link
                    to={`/product/${product.product_id}`}
                    className="font-bold text-base leading-tight line-clamp-2 hover:text-primary transition-colors text-text-main dark:text-white"
                  >
                    {product.name}
                  </Link>
                  {product.acceleration_bonus > 0 && (
                    <span className="material-symbols-outlined text-success text-[20px] bg-success/10 rounded-full p-1 ml-2 flex-shrink-0">
                      trending_up
                    </span>
                  )}
                </div>
                <p className="text-xs text-text-muted mb-4">
                  {product.category || "Geral"}
                </p>

                <div className="mt-auto pt-4 border-t border-outline dark:border-outline/20 flex items-center justify-between gap-3">
                  <select
                    value={product.status}
                    onChange={(e) =>
                      updateStatus(product.product_id, e.target.value)
                    }
                    className={`w-[130px] text-xs font-bold py-1.5 px-2 rounded-md border text-center appearance-none cursor-pointer outline-none transition-colors ${getStatusColor(product.status)} border-transparent focus:border-primary`}
                  >
                    <option value="planejando">Planejando</option>
                    <option value="gravando">Gravando</option>
                    <option value="publicado">Publicado</option>
                  </select>

                  <div className="w-16 h-6 opacity-60 group-hover:opacity-100 transition-opacity flex items-center">
                    <svg
                      className="w-full h-8 overflow-visible"
                      viewBox="0 0 64 24"
                    >
                      <path
                        className="stroke-dashoffset-100 group-hover:stroke-dashoffset-0 transition-all duration-1000 ease-in-out"
                        d="M0,20 L10,15 L20,18 L30,10 L40,12 L50,5 L64,2"
                        fill="none"
                        stroke={
                          product.final_score >= 80 ? "#00E676" : "#FFD54F"
                        }
                        strokeDasharray="100"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                      />
                    </svg>
                  </div>
                </div>
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
