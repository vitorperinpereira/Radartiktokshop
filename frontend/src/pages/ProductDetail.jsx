import { useState } from "react";
import { useParams, Link } from "react-router-dom";
import { useProduct } from "../hooks/useProduct";
import { useGarage } from "../hooks/useGarage";
import { formatCurrency } from "../utils/formatters";
import { ClassificationBadge } from "../components/dashboard/ClassificationBadge";
import { RiskFlags } from "../components/dashboard/RiskFlags";
import { SnapshotCard } from "../components/dashboard/SnapshotCard";
import { SubScoreRadar } from "../components/dashboard/SubScoreRadar";
import { ExplainabilitySummary } from "../components/dashboard/ExplainabilitySummary";
import { AgentReasoningTabs } from "../components/dashboard/AgentReasoningTabs";
import { ScoreBreakdown } from "../components/dashboard/ScoreBreakdown";
import { VideoModal } from "../components/VideoModal";

export function ProductDetail() {
  const { id } = useParams();
  const { product: data, loading, error } = useProduct(id);
  const { isSaved, saveProduct, removeProduct } = useGarage();
  const [showVideoModal, setShowVideoModal] = useState(false);

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center min-h-[50vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-primary"></div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-8">
        <div className="bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 p-6 rounded-lg border border-red-200 dark:border-red-800">
          <h2 className="font-bold text-lg mb-2">Erro ao carregar produto</h2>
          <p>
            {error || "Produto nao encontrado"}. Recarregue a pagina ou volte ao
            Radar.
          </p>
          <Link
            to="/"
            className="inline-flex items-center gap-2 mt-4 text-primary font-medium hover:underline"
          >
            <span className="material-symbols-outlined">arrow_back</span> Voltar
            ao Radar
          </Link>
        </div>
      </div>
    );
  }

  const product = data.product || data;
  const score = data.score || {};
  const latestSnapshot = data.latest_snapshot;
  const explainability = score.explainability_payload || {};
  const explainabilityScores = explainability.scores || {};

  const finalScore = Number(
    score.final_score || product.final_score || 0,
  ).toFixed(0);
  const trendScore = Number(score.trend_score || 0);
  const viralScore = Number(score.viral_potential_score || 0);
  const accessibilityScore = Number(score.creator_accessibility_score || 0);
  const revenueEstimate = Number(score.revenue_estimate || 0);
  const monetizationScore = Number(explainabilityScores.monetization || 0);
  const classification = score.classification || product.classification;
  const riskFlags = score.risk_flags || [];
  const saturationPenalty = Number(score.saturation_penalty || 0);
  const saturationPercentage = Math.min(saturationPenalty / 15, 1);
  const needleRotation = -90 + saturationPercentage * 180;

  const productId = product.id || product.product_id || id;
  const productName = product.title || product.name || "";

  const garageProduct = {
    product_id: productId,
    name: productName,
    category: product.category,
    image_url: product.image_url,
    final_score: score.final_score,
  };

  return (
    <div className="px-4 py-6 md:px-8 max-w-5xl mx-auto w-full pb-24 md:pb-8 relative">
      <div className="mb-6">
        <Link
          to="/"
          className="inline-flex items-center gap-1 text-sm text-text-muted hover:text-primary transition-colors"
        >
          <span className="material-symbols-outlined text-[18px]">
            arrow_back
          </span>
          Voltar ao Radar
        </Link>
      </div>

      {/* Page Header */}
      <div className="mb-8 flex flex-col md:flex-row md:items-start justify-between gap-4">
        <div className="flex gap-4 items-start">
          <div className="w-20 h-20 rounded-lg bg-outline/30 dark:bg-surface-dark flex-shrink-0 overflow-hidden shadow-sm">
            <img
              alt={productName}
              className="w-full h-full object-cover"
              src={
                product.image_url
                  ? `https://wsrv.nl/?url=${encodeURIComponent(product.image_url)}&default=${encodeURIComponent("https://placehold.co/200x200")}`
                  : "https://placehold.co/200x200"
              }
            />
          </div>
          <div>
            <div className="flex items-center gap-2 mb-1 flex-wrap">
              <span className="bg-outline/30 dark:bg-surface-dark text-text-muted text-xs font-semibold px-2.5 py-1 rounded-full uppercase tracking-wide">
                {product.category || "Geral"}
              </span>
              <ClassificationBadge classification={classification} />
            </div>
            <h2 className="text-2xl md:text-3xl font-bold text-text-main dark:text-white leading-tight mb-2">
              {productName}
            </h2>
            {riskFlags.length > 0 && (
              <div className="mt-2">
                <RiskFlags flags={riskFlags} />
              </div>
            )}
          </div>
        </div>

        <div className="flex flex-col items-end shrink-0 hidden md:flex">
          <div className="text-sm font-medium text-text-muted mb-1">
            Opportunity Score
          </div>
          <div className="flex items-baseline gap-1">
            <span
              className={`text-4xl font-black ${finalScore >= 80 ? "text-success" : finalScore >= 60 ? "text-warning" : "text-danger"}`}
            >
              {finalScore}
            </span>
            <span className="text-text-muted font-medium">/100</span>
          </div>
        </div>
      </div>

      {/* Two Column Layout */}
      <div className="flex flex-col lg:flex-row gap-6 lg:gap-8 flex-1">
        {/* Left Column */}
        <div className="w-full lg:w-3/5 flex flex-col gap-6">
          {/* Sub-Score Radar */}
          <div className="bg-surface dark:bg-surface-dark p-6 rounded-lg shadow-soft border border-outline dark:border-outline/20">
            <h3 className="text-lg font-bold flex items-center gap-2 text-text-main dark:text-white mb-4">
              <span className="material-symbols-outlined text-primary">
                analytics
              </span>
              Sub-Scores
            </h3>
            <SubScoreRadar
              trendScore={trendScore}
              viralScore={viralScore}
              accessibilityScore={accessibilityScore}
              monetizationScore={monetizationScore}
            />
          </div>

          {/* Metrics Cards */}
          <h3 className="text-lg font-bold flex items-center gap-2 text-text-main dark:text-white">
            <span className="material-symbols-outlined text-primary">
              grid_view
            </span>
            Metricas de Oportunidade
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="bg-surface dark:bg-surface-dark p-6 rounded-lg shadow-soft border border-outline dark:border-outline/20 flex flex-col justify-between h-[150px] hover:shadow-hover hover:-translate-y-1 transition-all">
              <div className="flex items-center justify-between text-text-muted mb-2">
                <span className="text-sm font-medium uppercase tracking-wider">
                  Tendencia
                </span>
                <span className="material-symbols-outlined text-muted">
                  trending_up
                </span>
              </div>
              <div>
                <div className="text-3xl font-black text-text-main dark:text-white">
                  {trendScore.toFixed(0)}/100
                </div>
                <div className="text-sm text-success flex items-center gap-1 mt-1">
                  <span className="material-symbols-outlined text-[16px]">
                    show_chart
                  </span>
                  Score de tendencia
                </div>
              </div>
            </div>

            <div className="bg-surface dark:bg-surface-dark p-6 rounded-lg shadow-soft border border-outline dark:border-outline/20 flex flex-col justify-between h-[150px] hover:shadow-hover hover:-translate-y-1 transition-all">
              <div className="flex items-center justify-between text-text-muted mb-2">
                <span className="text-sm font-medium uppercase tracking-wider">
                  Comissoes
                </span>
                <span className="material-symbols-outlined text-muted">
                  payments
                </span>
              </div>
              <div>
                <div className="text-3xl font-black text-text-main dark:text-white">
                  {formatCurrency(revenueEstimate)}
                </div>
                <div className="text-sm text-text-muted mt-1">
                  Estimativa semanal
                </div>
              </div>
            </div>

            <div className="bg-surface dark:bg-surface-dark p-6 rounded-lg shadow-soft border border-outline dark:border-outline/20 flex flex-col justify-between h-[150px] hover:shadow-hover hover:-translate-y-1 transition-all">
              <div className="flex items-center justify-between text-text-muted mb-2">
                <span className="text-sm font-medium uppercase tracking-wider">
                  Viral
                </span>
                <span className="material-symbols-outlined text-muted">
                  local_fire_department
                </span>
              </div>
              <div>
                <div className="text-3xl font-black text-text-main dark:text-white">
                  {viralScore.toFixed(0)}/100
                </div>
                <div className="text-sm text-text-muted mt-1">
                  Potencial viral
                </div>
              </div>
            </div>

            <div className="bg-surface dark:bg-surface-dark p-6 rounded-lg shadow-soft border border-outline dark:border-outline/20 flex flex-col justify-between h-[150px] hover:shadow-hover hover:-translate-y-1 transition-all">
              <div className="flex items-center justify-between text-text-muted mb-2">
                <span className="text-sm font-medium uppercase tracking-wider">
                  Acessibilidade
                </span>
                <span className="material-symbols-outlined text-muted">
                  group
                </span>
              </div>
              <div>
                <div className="text-3xl font-black text-text-main dark:text-white">
                  {accessibilityScore.toFixed(0)}/100
                </div>
                <div className="text-sm text-text-muted mt-1">
                  Para criadores
                </div>
              </div>
            </div>
          </div>

          {/* Explainability Summary */}
          <ExplainabilitySummary explainabilityPayload={explainability} />

          {/* Agent Reasoning Tabs */}
          <AgentReasoningTabs explainabilityPayload={explainability} />

          {/* Snapshot Card */}
          <SnapshotCard snapshot={latestSnapshot} />

          {/* Score Breakdown */}
          <div className="bg-surface dark:bg-surface-dark rounded-lg shadow-soft border border-outline dark:border-outline/20 overflow-hidden">
            <h3 className="text-lg font-bold flex items-center gap-2 text-text-main dark:text-white p-6 pb-0">
              <span className="material-symbols-outlined text-primary">
                bar_chart
              </span>
              Detalhamento do Score
            </h3>
            <ScoreBreakdown
              entry={{
                trend_score: trendScore,
                viral_score: viralScore,
                creator_accessibility_score: accessibilityScore,
                monetization_score: monetizationScore,
                acceleration_bonus: score.acceleration_bonus,
                estimated_weekly_commission: revenueEstimate,
                days_since_detected: score.days_since_detected,
              }}
            />
          </div>
        </div>

        {/* Right Column: Saturation */}
        <div className="w-full lg:w-2/5 flex flex-col gap-6">
          <div className="bg-surface dark:bg-surface-dark p-6 rounded-lg shadow-soft border border-outline dark:border-outline/20 flex-1 flex flex-col items-center justify-center text-center">
            <h3 className="text-lg font-bold w-full text-left flex items-center gap-2 mb-8 text-text-main dark:text-white">
              <span className="material-symbols-outlined text-primary">
                speed
              </span>
              Termometro de Saturacao
            </h3>

            <div className="gauge-container mb-6">
              <div className="gauge-background"></div>
              <div
                className="gauge-needle"
                style={{
                  transform: `rotate(${needleRotation}deg) translateX(-50%)`,
                }}
              ></div>
            </div>

            <div className="flex justify-between w-[240px] text-xs font-semibold uppercase text-text-muted tracking-wide mb-6">
              <span className="text-success">Baixo</span>
              <span className="text-warning">Medio</span>
              <span className="text-danger">Saturado</span>
            </div>

            <div
              className={`inline-flex items-center gap-2 px-4 py-2 rounded-full font-bold text-sm ${
                saturationPercentage < 0.33
                  ? "bg-success/10 text-success"
                  : saturationPercentage > 0.66
                    ? "bg-danger/10 text-danger"
                    : "bg-warning/10 text-warning"
              }`}
            >
              <span className="material-symbols-outlined text-[18px]">
                {saturationPercentage < 0.33
                  ? "check_circle"
                  : saturationPercentage > 0.66
                    ? "warning"
                    : "info"}
              </span>
              {saturationPercentage < 0.33
                ? "Baixo Risco"
                : saturationPercentage > 0.66
                  ? "Alto Risco"
                  : "Atencao Necessaria"}
            </div>

            <p className="text-sm text-text-muted mt-4 max-w-[280px]">
              Penalidade de saturacao:{" "}
              <strong>{saturationPenalty.toFixed(1)}</strong>/15.
              {saturationPercentage < 0.5
                ? " O mercado ainda tem espaco para novos videos deste produto."
                : " Ja esta saturado, encontre angulos unicos para se destacar."}
            </p>
          </div>

          <div className="hidden md:flex flex-col gap-3">
            <button
              onClick={() => setShowVideoModal(true)}
              className="w-full bg-gray-900 dark:bg-surface-dark hover:bg-gray-800 dark:hover:bg-surface-dark/80 text-white font-bold py-4 px-6 rounded-lg shadow-lg transition-all flex items-center justify-center gap-2 text-base border border-gray-700"
            >
              <span className="material-symbols-outlined">play_circle</span>
              Ver Videos do Produto
            </button>

            <Link
              to={`/ideas?product=${productId}`}
              className="w-full bg-primary hover:bg-primary/90 text-white font-bold py-4 px-6 rounded-lg shadow-lg hover:shadow-primary/30 transition-all flex items-center justify-center gap-2 text-base"
            >
              <span className="material-symbols-outlined">auto_fix_high</span>
              Gerar Angulo de Conteudo
            </Link>

            <button
              onClick={() =>
                isSaved(productId)
                  ? removeProduct(productId)
                  : saveProduct(garageProduct)
              }
              className={`w-full font-bold py-4 px-6 rounded-lg transition-all flex items-center justify-center gap-2 text-base border ${
                isSaved(productId)
                  ? "bg-surface dark:bg-surface-dark border-outline dark:border-outline/20 text-text-main dark:text-white hover:bg-red-50 dark:hover:bg-red-900/20 hover:text-danger hover:border-danger"
                  : "bg-surface dark:bg-surface-dark border-primary text-primary hover:bg-primary/5"
              }`}
            >
              <span className="material-symbols-outlined">
                {isSaved(productId) ? "remove_done" : "garage"}
              </span>
              {isSaved(productId) ? "Remover da Garagem" : "Salvar na Garagem"}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Sticky CTA */}
      <div className="md:hidden fixed bottom-0 left-0 right-0 p-4 bg-surface/80 dark:bg-surface-dark/80 backdrop-blur-md border-t border-outline dark:border-outline/20 z-50 flex gap-2">
        <button
          onClick={() => setShowVideoModal(true)}
          className="flex-1 bg-gray-900 text-white font-bold py-3.5 px-4 rounded-lg flex items-center justify-center gap-2 text-sm"
        >
          <span className="material-symbols-outlined">play_circle</span>
          Videos
        </button>
        <Link
          to={`/ideas?product=${productId}`}
          className="flex-1 bg-primary hover:bg-primary/90 text-white font-bold py-3.5 px-4 rounded-lg shadow-lg flex items-center justify-center gap-2 text-sm transition-transform active:scale-95"
        >
          <span className="material-symbols-outlined">auto_fix_high</span>
          Angulos
        </Link>
      </div>

      {/* Video Modal */}
      <VideoModal
        productId={productId}
        productName={productName}
        isOpen={showVideoModal}
        onClose={() => setShowVideoModal(false)}
      />
    </div>
  );
}
