"""GMV estimation from inventory deltas across snapshots."""

from __future__ import annotations

from decimal import Decimal


def estimate_gmv_from_snapshots(
    snapshots: list[dict[str, object]],
) -> Decimal | None:
    """Estimate GMV via delta of inventory between consecutive snapshots."""

    if len(snapshots) < 2:
        return None

    total_gmv = Decimal("0")
    valid_pairs = 0
    for index in range(1, len(snapshots)):
        previous = snapshots[index - 1]
        current = snapshots[index]
        prev_stock = previous.get("stock_count")
        curr_stock = current.get("stock_count")
        price = current.get("price")

        if prev_stock is None or curr_stock is None or price is None:
            continue

        valid_pairs += 1
        delta = max(0, int(prev_stock) - int(curr_stock))
        total_gmv += Decimal(str(delta)) * Decimal(str(price))

    return None if valid_pairs == 0 else total_gmv
