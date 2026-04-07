import { useEffect, useState } from "react";
import { getScoreGradient, getAccelerationIcon } from "../../utils/scoreColors";
import { formatCurrency, formatDaysAgo } from "../../utils/formatters";

function ScoreBar({ label, score }) {
  const [width, setWidth] = useState(0);

  useEffect(() => {
    const timer = setTimeout(() => setWidth(Number(score) || 0), 100);
    return () => clearTimeout(timer);
  }, [score]);

  return (
    <div className="flex items-center gap-3 mb-2">
      <span className="w-24 text-sm text-text-muted">{label}</span>
      <div className="flex-1 h-3 bg-outline/30 dark:bg-surface-dark rounded overflow-hidden">
        <div
          className="h-full rounded transition-all duration-600 ease-out"
          style={{ width: `${width}%`, background: getScoreGradient(score) }}
        />
      </div>
      <span className="w-10 text-right text-sm font-bold text-text-main dark:text-white">
        {Number(score || 0).toFixed(1)}
      </span>
    </div>
  );
}

export function ScoreBreakdown({ entry }) {
  if (!entry) return null;

  const trendScore = entry.trend_score ?? entry.trendScore ?? 0;
  const viralScore =
    entry.viral_score ?? entry.viralScore ?? entry.viral_potential_score ?? 0;
  const accessibilityScore =
    entry.creator_accessibility_score ?? entry.accessibility_score ?? 0;
  const monetizationScore =
    entry.monetization_score ??
    entry.monetizationScore ??
    entry.revenue_score ??
    0;
  const accelerationBonus = entry.acceleration_bonus;
  const daysSinceDetected = entry.days_since_detected;
  const hasAcceleration =
    accelerationBonus !== null && accelerationBonus !== undefined;
  const hasDaysSinceDetected =
    daysSinceDetected !== null && daysSinceDetected !== undefined;

  return (
    <div className="p-4 bg-outline/30 dark:bg-surface-dark border-t border-outline dark:border-outline/20 space-y-4">
      <div>
        <ScoreBar label="Tendencia" score={trendScore} />
        <ScoreBar label="Monetizacao" score={monetizationScore} />
        <ScoreBar label="Acessibilidade" score={accessibilityScore} />
        <ScoreBar label="Viral" score={viralScore} />
      </div>

      <div className="flex flex-wrap gap-4 pt-3 border-t border-outline dark:border-outline/20 text-sm text-text-main dark:text-muted">
        <span>
          {hasAcceleration ? (
            <>
              {getAccelerationIcon(accelerationBonus)} Aceleracao:{" "}
              <span className="text-text-muted">
                {Number(accelerationBonus).toFixed(2)}x
              </span>
            </>
          ) : (
            <>
              Aceleracao: <span className="text-text-muted">n/a</span>
            </>
          )}
        </span>
        <span>
          Comissao est.:{" "}
          <span className="text-success font-bold">
            {formatCurrency(entry.estimated_weekly_commission)}
          </span>
          /sem
        </span>
        <span>
          Detectado:{" "}
          <span className="text-text-muted">
            {hasDaysSinceDetected ? formatDaysAgo(daysSinceDetected) : "n/a"}
          </span>
        </span>
      </div>
    </div>
  );
}
