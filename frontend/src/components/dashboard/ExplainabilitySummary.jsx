export function ExplainabilitySummary({ explainabilityPayload }) {
  if (!explainabilityPayload) return null;

  const summary =
    explainabilityPayload.summary ||
    explainabilityPayload.explanation?.summary ||
    null;

  const positiveSignals =
    explainabilityPayload.positive_signals ||
    explainabilityPayload.explanation?.positive_signals ||
    [];
  const negativeSignals =
    explainabilityPayload.negative_signals ||
    explainabilityPayload.explanation?.negative_signals ||
    [];

  if (!summary && positiveSignals.length === 0 && negativeSignals.length === 0)
    return null;

  return (
    <div className="bg-primary/5 dark:bg-primary/10 rounded-lg p-5 border border-primary/10">
      <h4 className="font-semibold text-text-main dark:text-white flex items-center gap-2 mb-3">
        <span className="material-symbols-outlined text-primary text-[20px]">
          lightbulb
        </span>
        Insight do Radar
      </h4>
      {summary && (
        <p className="text-sm text-text-muted leading-relaxed mb-4">
          {summary}
        </p>
      )}
      {(positiveSignals.length > 0 || negativeSignals.length > 0) && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {positiveSignals.map((signal, i) => (
            <div
              key={`pos-${i}`}
              className="flex items-start gap-2 bg-success/5 border border-success/10 rounded-md px-3 py-2"
            >
              <span
                className="material-symbols-outlined text-success mt-0.5"
                style={{ fontSize: "16px" }}
              >
                add_circle
              </span>
              <span className="text-sm text-text-main dark:text-muted">
                {typeof signal === "string"
                  ? signal
                  : signal.text || JSON.stringify(signal)}
              </span>
            </div>
          ))}
          {negativeSignals.map((signal, i) => (
            <div
              key={`neg-${i}`}
              className="flex items-start gap-2 bg-danger/5 border border-danger/10 rounded-md px-3 py-2"
            >
              <span
                className="material-symbols-outlined text-danger mt-0.5"
                style={{ fontSize: "16px" }}
              >
                remove_circle
              </span>
              <span className="text-sm text-text-main dark:text-muted">
                {typeof signal === "string"
                  ? signal
                  : signal.text || JSON.stringify(signal)}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
