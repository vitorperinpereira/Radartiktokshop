import { getLabelColor } from "../../utils/scoreColors";

export function LabelBadge({ label }) {
  if (!label) return null;
  const color = getLabelColor(label);

  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        padding: "2px 8px",
        borderRadius: "6px",
        backgroundColor: `${color}26`, // approx 15% opacity hex
        border: `1px solid ${color}`,
        color: color,
        fontWeight: "bold",
        textTransform: "uppercase",
        fontSize: "0.75rem",
        lineHeight: "1.2",
      }}
    >
      {label === "EXPLOSIVE" && "🔥 "}
      {label}
    </span>
  );
}
