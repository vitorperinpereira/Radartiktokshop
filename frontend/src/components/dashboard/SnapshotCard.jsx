import { formatCurrency, formatDate } from "../../utils/formatters";

export function SnapshotCard({ snapshot }) {
  if (!snapshot) {
    return (
      <div className="bg-surface dark:bg-surface-dark p-6 rounded-lg shadow-soft border border-outline dark:border-outline/20 text-center text-text-muted">
        <span className="material-symbols-outlined text-3xl mb-2 block">
          inventory_2
        </span>
        <p className="text-sm">Nenhum snapshot disponível</p>
      </div>
    );
  }

  const items = [
    {
      label: "Preço",
      value: snapshot.price != null ? formatCurrency(snapshot.price) : "N/A",
      icon: "sell",
    },
    {
      label: "Pedidos Est.",
      value:
        snapshot.orders_estimate != null
          ? snapshot.orders_estimate.toLocaleString("pt-BR")
          : "N/A",
      icon: "shopping_cart",
    },
    {
      label: "Avaliação",
      value:
        snapshot.rating != null
          ? `${Number(snapshot.rating).toFixed(1)} / 5.0`
          : "N/A",
      icon: "star",
    },
    {
      label: "Comissão",
      value:
        snapshot.commission_rate != null
          ? `${Number(snapshot.commission_rate).toFixed(1)}%`
          : "N/A",
      icon: "percent",
    },
  ];

  return (
    <div className="bg-surface dark:bg-surface-dark p-6 rounded-lg shadow-soft border border-outline dark:border-outline/20">
      <div className="flex items-center justify-between mb-4">
        <h4 className="font-semibold text-text-main dark:text-white flex items-center gap-2">
          <span className="material-symbols-outlined text-primary text-[20px]">
            camera
          </span>
          Último Snapshot
        </h4>
        {snapshot.captured_at && (
          <span className="text-xs text-text-muted">
            {formatDate(snapshot.captured_at)}
          </span>
        )}
      </div>
      <div className="grid grid-cols-2 gap-4">
        {items.map((item) => (
          <div key={item.label} className="flex items-center gap-3">
            <span
              className="material-symbols-outlined text-muted"
              style={{ fontSize: "20px" }}
            >
              {item.icon}
            </span>
            <div>
              <div className="text-xs text-text-muted uppercase tracking-wide">
                {item.label}
              </div>
              <div className="text-base font-bold text-text-main dark:text-white">
                {item.value}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
