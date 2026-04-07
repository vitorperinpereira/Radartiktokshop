import {
  getClassificationColor,
  getClassificationLabel,
} from "../../utils/scoreColors";

const ICONS = {
  EXPLOSIVE: "local_fire_department",
  HIGH: "trending_up",
  WORTH_TEST: "science",
  NICHE: "target",
  LOW: "arrow_downward",
};

export function ClassificationBadge({ classification }) {
  if (!classification) return null;

  const color = getClassificationColor(classification);
  const label = getClassificationLabel(classification);
  const icon = ICONS[classification] || "label";

  return (
    <span
      className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold uppercase tracking-wide"
      style={{
        backgroundColor: `${color}15`,
        color,
        border: `1px solid ${color}30`,
      }}
    >
      <span className="material-symbols-outlined" style={{ fontSize: "14px" }}>
        {icon}
      </span>
      {label}
    </span>
  );
}
