"""Deterministic feature extraction from the latest product snapshots."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from services.shared.db.models import Product, ProductSignal, ProductSnapshot
from services.workers.google_trends import fetch_trend_score

FEATURE_SOURCE_KIND = "weekly-bootstrap"


@dataclass(frozen=True)
class SignalCandidate:
    signal_name: str
    signal_value: Decimal
    signal_type: str
    observed_at: datetime
    evidence: dict[str, object]
    source_kind: str = FEATURE_SOURCE_KIND


@dataclass(frozen=True)
class FeatureExtractionSummary:
    latest_snapshots: int
    products_considered: int
    signals_created: int


def build_signal_candidates(snapshot: ProductSnapshot) -> list[SignalCandidate]:
    candidates: list[SignalCandidate] = []
    evidence_base = {
        "source_name": snapshot.source_name,
        "source_record_id": snapshot.source_record_id,
        "captured_at": snapshot.captured_at.isoformat(),
    }

    def add_candidate(
        signal_name: str,
        signal_type: str,
        signal_value: Decimal | int | None,
    ) -> None:
        if signal_value is None:
            return

        normalized_value = (
            signal_value if isinstance(signal_value, Decimal) else Decimal(str(signal_value))
        )
        candidates.append(
            SignalCandidate(
                signal_name=signal_name,
                signal_value=normalized_value,
                signal_type=signal_type,
                observed_at=snapshot.captured_at,
                evidence={**evidence_base, "metric": signal_name},
            )
        )

    add_candidate("price_current", "currency", snapshot.price)
    add_candidate("orders_estimate_current", "count", snapshot.orders_estimate)
    add_candidate("rating_current", "score", snapshot.rating)
    add_candidate("commission_rate_current", "percentage", snapshot.commission_rate)

    raw_stock_count = snapshot.raw_payload.get("stock_count")
    if isinstance(raw_stock_count, (int, float, str, Decimal)):
        add_candidate("stock_count", "count", raw_stock_count)

    if snapshot.price is not None and snapshot.orders_estimate is not None:
        add_candidate(
            "revenue_proxy_current",
            "currency",
            snapshot.price * Decimal(snapshot.orders_estimate),
        )

    return candidates


def _principal_keyword(title: str) -> str:
    tokens = [token for token in title.lower().replace("-", " ").split() if token]
    if not tokens:
        return title.strip().lower()
    filtered = [token for token in tokens if token not in {"de", "da", "do", "para", "com"}]
    candidate_tokens = filtered or tokens
    return " ".join(candidate_tokens[:3]).strip()


def _latest_snapshots(session: Session) -> list[ProductSnapshot]:
    snapshots = session.execute(
        select(ProductSnapshot).order_by(
            ProductSnapshot.product_id,
            ProductSnapshot.captured_at.desc(),
            ProductSnapshot.created_at.desc(),
        )
    ).scalars()

    latest_by_product: dict[str, ProductSnapshot] = {}
    for snapshot in snapshots:
        latest_by_product.setdefault(snapshot.product_id, snapshot)

    return list(latest_by_product.values())


def _signal_exists(
    session: Session,
    *,
    product_id: str,
    candidate: SignalCandidate,
) -> bool:
    existing = session.execute(
        select(ProductSignal).where(
            ProductSignal.product_id == product_id,
            ProductSignal.signal_name == candidate.signal_name,
            ProductSignal.observed_at == candidate.observed_at,
            ProductSignal.source_kind == candidate.source_kind,
        ).limit(1)
    ).scalar_one_or_none()
    return existing is not None


def extract_latest_snapshot_signals(session: Session) -> FeatureExtractionSummary:
    latest_snapshots = _latest_snapshots(session)
    signals_created = 0

    for snapshot in latest_snapshots:
        product = session.get(Product, snapshot.product_id)
        for candidate in build_signal_candidates(snapshot):
            if _signal_exists(session, product_id=snapshot.product_id, candidate=candidate):
                continue

            session.add(
                ProductSignal(
                    id=str(uuid4()),
                    product_id=snapshot.product_id,
                    signal_name=candidate.signal_name,
                    signal_value=candidate.signal_value,
                    signal_type=candidate.signal_type,
                    observed_at=candidate.observed_at,
                    evidence=candidate.evidence,
                    source_kind=candidate.source_kind,
                    created_at=datetime.now(candidate.observed_at.tzinfo),
                )
            )
            signals_created += 1

        if product is not None:
            keyword = _principal_keyword(product.title)
            google_trends_score = fetch_trend_score(keyword)
            if google_trends_score is not None:
                trend_candidate = SignalCandidate(
                    signal_name="google_trends_score",
                    signal_value=Decimal(str(google_trends_score)),
                    signal_type="score",
                    observed_at=snapshot.captured_at,
                    evidence={
                        "source_name": snapshot.source_name,
                        "source_record_id": snapshot.source_record_id,
                        "captured_at": snapshot.captured_at.isoformat(),
                        "metric": "google_trends_score",
                        "keyword": keyword,
                        "geo": "BR",
                        "timeframe": "now 7-d",
                    },
                )
                if not _signal_exists(
                    session,
                    product_id=snapshot.product_id,
                    candidate=trend_candidate,
                ):
                    session.add(
                        ProductSignal(
                            id=str(uuid4()),
                            product_id=snapshot.product_id,
                            signal_name=trend_candidate.signal_name,
                            signal_value=trend_candidate.signal_value,
                            signal_type=trend_candidate.signal_type,
                            observed_at=trend_candidate.observed_at,
                            evidence=trend_candidate.evidence,
                            source_kind=trend_candidate.source_kind,
                            created_at=datetime.now(trend_candidate.observed_at.tzinfo),
                        )
                    )
                    signals_created += 1

    return FeatureExtractionSummary(
        latest_snapshots=len(latest_snapshots),
        products_considered=len(latest_snapshots),
        signals_created=signals_created,
    )
