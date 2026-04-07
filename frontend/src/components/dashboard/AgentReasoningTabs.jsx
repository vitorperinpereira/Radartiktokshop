import { useState } from "react";

const TABS = [
  { key: "trend", label: "Tendência", icon: "trending_up" },
  { key: "viral", label: "Viral", icon: "local_fire_department" },
  { key: "accessibility", label: "Acessibilidade", icon: "group" },
];

function ReasoningPanel({ reasoning }) {
  if (!reasoning) {
    return (
      <p className="text-sm text-text-muted italic">
        Nenhuma análise disponível para este agente.
      </p>
    );
  }

  const strengths = reasoning.strengths || reasoning.positive_signals || [];
  const weaknesses = reasoning.weaknesses || reasoning.negative_signals || [];
  const evidence = reasoning.evidence || reasoning.raw_evidence || [];

  return (
    <div className="space-y-4">
      {strengths.length > 0 && (
        <div>
          <h5 className="text-sm font-semibold text-success flex items-center gap-1 mb-2">
            <span
              className="material-symbols-outlined"
              style={{ fontSize: "16px" }}
            >
              thumb_up
            </span>
            Pontos Fortes
          </h5>
          <ul className="space-y-1">
            {strengths.map((s, i) => (
              <li
                key={i}
                className="text-sm text-text-main dark:text-muted flex items-start gap-2"
              >
                <span className="text-success mt-0.5">+</span>
                {typeof s === "string" ? s : s.text || JSON.stringify(s)}
              </li>
            ))}
          </ul>
        </div>
      )}
      {weaknesses.length > 0 && (
        <div>
          <h5 className="text-sm font-semibold text-danger flex items-center gap-1 mb-2">
            <span
              className="material-symbols-outlined"
              style={{ fontSize: "16px" }}
            >
              thumb_down
            </span>
            Pontos Fracos
          </h5>
          <ul className="space-y-1">
            {weaknesses.map((w, i) => (
              <li
                key={i}
                className="text-sm text-text-main dark:text-muted flex items-start gap-2"
              >
                <span className="text-danger mt-0.5">-</span>
                {typeof w === "string" ? w : w.text || JSON.stringify(w)}
              </li>
            ))}
          </ul>
        </div>
      )}
      {evidence.length > 0 && (
        <div>
          <h5 className="text-sm font-semibold text-text-muted flex items-center gap-1 mb-2">
            <span
              className="material-symbols-outlined"
              style={{ fontSize: "16px" }}
            >
              description
            </span>
            Evidências
          </h5>
          <ul className="space-y-1">
            {evidence.map((e, i) => (
              <li
                key={i}
                className="text-xs text-text-muted bg-outline/30 dark:bg-surface-dark px-3 py-2 rounded"
              >
                {typeof e === "string" ? e : JSON.stringify(e)}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export function AgentReasoningTabs({ explainabilityPayload }) {
  const [activeTab, setActiveTab] = useState("trend");

  if (!explainabilityPayload) return null;

  const agents =
    explainabilityPayload.agent_reasoning || explainabilityPayload.agents || {};

  return (
    <div className="bg-surface dark:bg-surface-dark rounded-lg shadow-soft border border-outline dark:border-outline/20 overflow-hidden">
      <div className="flex border-b border-outline dark:border-outline/20">
        {TABS.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 text-sm font-medium transition-colors ${
              activeTab === tab.key
                ? "text-primary border-b-2 border-primary bg-primary/5"
                : "text-text-muted hover:text-text-main dark:hover:text-white hover:bg-outline/30 dark:hover:bg-surface-dark/80"
            }`}
          >
            <span
              className="material-symbols-outlined"
              style={{ fontSize: "18px" }}
            >
              {tab.icon}
            </span>
            <span className="hidden sm:inline">{tab.label}</span>
          </button>
        ))}
      </div>
      <div className="p-5">
        <ReasoningPanel reasoning={agents[activeTab]} />
      </div>
    </div>
  );
}
