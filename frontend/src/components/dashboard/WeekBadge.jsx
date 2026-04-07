export function WeekBadge({ weekLabel, week_label }) {
  const resolvedWeekLabel = weekLabel || week_label;
  if (!resolvedWeekLabel) return null;

  let display = resolvedWeekLabel;
  const match = resolvedWeekLabel.match(/^(\d{4})-W(\d{1,2})$/);
  if (match) {
    display = `Semana ${match[2]} | ${match[1]}`;
  }

  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        padding: "4px 12px",
        borderRadius: "6px",
        backgroundColor: "#2A2A2A",
        color: "#A0A0A0",
        fontSize: "0.85rem",
        fontWeight: "500",
      }}
    >
      Sem. {display}
    </span>
  );
}
