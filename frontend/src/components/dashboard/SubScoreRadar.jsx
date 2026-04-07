import { useEffect, useState } from "react";

const SCORES = [
  { key: "trend", label: "Tendência", weight: "35%", color: "#00E676" },
  { key: "viral", label: "Viral", weight: "30%", color: "#FF0050" },
  {
    key: "accessibility",
    label: "Acessibilidade",
    weight: "25%",
    color: "#00F2FE",
  },
  {
    key: "monetization",
    label: "Monetização",
    weight: "10%",
    color: "var(--color-warning)",
  },
];

export function SubScoreRadar({
  trendScore,
  viralScore,
  accessibilityScore,
  monetizationScore,
}) {
  const [animated, setAnimated] = useState(false);

  useEffect(() => {
    const t = setTimeout(() => setAnimated(true), 100);
    return () => clearTimeout(t);
  }, []);

  const values = {
    trend: Number(trendScore) || 0,
    viral: Number(viralScore) || 0,
    accessibility: Number(accessibilityScore) || 0,
    monetization: Number(monetizationScore) || 0,
  };

  return (
    <div className="space-y-3">
      {SCORES.map(({ key, label, weight, color }) => (
        <div key={key} className="flex items-center gap-3">
          <div className="w-28 flex items-center justify-between">
            <span className="text-sm font-medium text-text-main dark:text-muted">
              {label}
            </span>
            <span className="text-xs text-text-muted ml-1">{weight}</span>
          </div>
          <div className="flex-1 h-3 bg-outline/30 dark:bg-surface-dark rounded-full overflow-hidden">
            <div
              className="h-full rounded-full transition-all duration-700 ease-out"
              style={{
                width: animated ? `${values[key]}%` : "0%",
                backgroundColor: color,
              }}
            />
          </div>
          <span className="w-10 text-right text-sm font-bold text-text-main dark:text-white">
            {values[key].toFixed(0)}
          </span>
        </div>
      ))}
    </div>
  );
}
