import { getRiskFlagIcon } from "../../utils/scoreColors";

const FLAG_LABELS = {
  high_saturation: "Alta Saturação",
  weak_evidence: "Evidência Fraca",
  price_volatility: "Preço Volátil",
  low_creator_count: "Poucos Criadores",
  declining_trend: "Tendência em Queda",
  short_history: "Histórico Curto",
};

export function RiskFlags({ flags = [] }) {
  if (!flags || flags.length === 0) return null;

  return (
    <div className="flex flex-wrap gap-2">
      {flags.map((flag) => (
        <span
          key={flag}
          className="inline-flex items-center gap-1 px-2 py-1 rounded-md text-xs font-medium bg-danger/10 text-danger border border-danger/20"
        >
          <span
            className="material-symbols-outlined"
            style={{ fontSize: "14px" }}
          >
            {getRiskFlagIcon(flag)}
          </span>
          {FLAG_LABELS[flag] || flag}
        </span>
      ))}
    </div>
  );
}
