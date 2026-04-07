from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from apps.api.deps import get_session

from .service import RankingApiService

router = APIRouter()


class _RankingServiceProxy:
    def __init__(self) -> None:
        self._service: RankingApiService | None = None

    def bind(self, session: Session) -> "_RankingServiceProxy":
        self._service = RankingApiService(session)
        return self

    def _require_service(self) -> RankingApiService:
        if self._service is None:
            raise RuntimeError("ranking_service is not bound to a database session")
        return self._service

    def get_latest_report(self):
        return self._require_service().get_latest_report()

    def get_product_entry(self, product_id: str):
        return self._require_service().get_product_entry(product_id)


ranking_service = _RankingServiceProxy()


def get_service(
    session: Annotated[Session, Depends(get_session)],
) -> _RankingServiceProxy:
    return ranking_service.bind(session)


@router.get("/latest")
def get_latest(
    service: Annotated[_RankingServiceProxy, Depends(get_service)],
):
    report = service.get_latest_report()
    if not report:
        raise HTTPException(status_code=404, detail="Nenhum ranking disponivel ainda")
    return report


@router.get("/latest/entries")
def get_latest_entries(
    service: Annotated[_RankingServiceProxy, Depends(get_service)],
    category: str | None = Query(None),
    label: str | None = Query(None),
    classification: str | None = Query(None),
    min_score: float | None = Query(None),
    sort_by: str = Query("final_score"),
    order: str = Query("desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
):
    report = service.get_latest_report()
    if not report:
        raise HTTPException(status_code=404, detail="Nenhum ranking disponivel ainda")

    entries = list(report.entries)

    # Hard filter: BR only
    entries = [
        e
        for e in entries
        if (getattr(e, "region", None) or "BR").upper() == "BR"
    ]

    resolved_label = classification or label

    if category:
        entries = [e for e in entries if getattr(e, "category", None) == category]
    if resolved_label:
        entries = [e for e in entries if getattr(e, "label", None) == resolved_label]
    if min_score is not None:
        entries = [e for e in entries if getattr(e, "final_score", 0.0) >= min_score]

    reverse = order.lower() == "desc"

    def sort_key(e):
        return getattr(e, sort_by, 0.0) or 0.0

    try:
        entries.sort(key=sort_key, reverse=reverse)
    except Exception:
        entries.sort(key=lambda e: getattr(e, "final_score", 0.0), reverse=True)

    total = len(entries)
    start = (page - 1) * page_size
    end = start + page_size

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "entries": entries[start:end],
    }


@router.get("/latest/entries/{product_id}")
def get_entry(
    service: Annotated[_RankingServiceProxy, Depends(get_service)],
    product_id: str,
):
    entry = service.get_product_entry(product_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Produto nao encontrado no ranking")
    return entry


@router.get("/meta")
def get_meta(
    service: Annotated[_RankingServiceProxy, Depends(get_service)],
):
    report = service.get_latest_report()
    if not report:
        raise HTTPException(status_code=404, detail="Nenhum ranking disponivel ainda")

    categories = set()
    labels = set()
    for entry in report.entries:
        if getattr(entry, "category", None):
            categories.add(entry.category)
        if getattr(entry, "label", None):
            labels.add(entry.label)

    return {
        "week_label": getattr(report, "week_label", "Desconhecida"),
        "generated_at": getattr(report, "generated_at", None),
        "total_products": len(report.entries),
        "available_categories": sorted(categories),
        "available_labels": sorted(labels),
    }
