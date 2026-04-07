"""Generate ranking cache JSON for the ranking API endpoints."""

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from services.shared.config import ROOT_DIR, get_settings
from services.shared.db.session import build_session_factory
from services.shared.db.models import Product, ProductScore, ProductSnapshot


def main() -> None:
    sf = build_session_factory(settings=get_settings())

    with sf() as s:
        scores = (
            s.query(ProductScore)
            .order_by(ProductScore.final_score.desc())
            .all()
        )
        if not scores:
            print("No scores found. Run seed_mock_scores.py first.")
            return

        entries = []
        for rank, sc in enumerate(scores, 1):
            prod = s.query(Product).filter(Product.id == sc.product_id).first()
            if not prod:
                continue

            snap = (
                s.query(ProductSnapshot)
                .filter(ProductSnapshot.product_id == prod.id)
                .order_by(ProductSnapshot.captured_at.desc())
                .first()
            )

            commission_rate = float(snap.commission_rate or 10) if snap else 10.0
            price = float(snap.price or 30) if snap else 30.0
            orders = int(snap.orders_estimate or 50) if snap else 50
            est_commission = price * (commission_rate / 100) * orders * 0.3

            # revenue_score must be 0-100, normalize from revenue_estimate
            raw_rev = float(sc.revenue_estimate or 0)
            revenue_score = min(raw_rev / 5, 100.0)

            entries.append({
                "rank": rank,
                "product_id": prod.id,
                "name": prod.title,
                "category": prod.category or "General",
                "final_score": float(sc.final_score or 0),
                "label": sc.classification or "WORTH_TEST",
                "trend_score": float(sc.trend_score or 0),
                "revenue_score": round(revenue_score, 2),
                "competition_score": float(sc.creator_accessibility_score or 0),
                "viral_score": float(sc.viral_potential_score or 0),
                "decay_factor": 0.95,
                "acceleration_bonus": 1.15 if rank == 1 else 1.05 if rank == 2 else 1.0,
                "estimated_weekly_commission": round(est_commission, 2),
                "days_since_detected": 3 * rank,
                "scored_at": datetime.now(timezone.utc).isoformat(),
            })

        week_label = f"{sc.week_start.year}-W{sc.week_start.isocalendar()[1]:02d}"

        report = {
            "report_id": str(uuid4()),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "week_label": week_label,
            "total_products_analyzed": len(entries),
            "top_n": len(entries),
            "filters_applied": {},
            "params_used": {},
            "entries": entries,
        }

        cache_dir = ROOT_DIR / ".cache" / "ranking"
        cache_dir.mkdir(parents=True, exist_ok=True)
        out_path = cache_dir / f"ranking_{week_label}.json"
        out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Written {len(entries)} entries to {out_path}")


if __name__ == "__main__":
    main()
