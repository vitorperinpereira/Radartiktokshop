"""Router for Garage functionality, allowing creators to save products."""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from apps.api.deps import get_session
from services.shared.db.models import GarageItem, Product

router = APIRouter(tags=["garage"])


class GarageItemCreate(BaseModel):
    product_id: str


class GarageItemUpdateStatus(BaseModel):
    status: str


class GarageItemResponse(BaseModel):
    id: str
    product_id: str
    status: str
    saved_at: datetime

    # Enriched fields for the frontend
    name: str | None = None
    category: str | None = None
    image_url: str | None = None
    final_score: float | None = None

    class Config:
        from_attributes = True


def _latest_score(product: Product) -> float | None:
    if not product.scores:
        return None
    latest = sorted(product.scores, key=lambda s: s.week_start, reverse=True)[0]
    return float(latest.final_score) if latest.final_score else None


def _enrich(resp: GarageItemResponse, product: Product) -> GarageItemResponse:
    resp.name = product.title
    resp.category = product.category
    resp.image_url = product.image_url
    resp.final_score = _latest_score(product)
    return resp


@router.get("/garage", response_model=list[GarageItemResponse])
def get_garage_items(session: Session = Depends(get_session)):  # noqa: B008
    items = session.query(GarageItem).order_by(GarageItem.saved_at.desc()).all()
    results = []
    for item in items:
        resp = GarageItemResponse.model_validate(item)
        if item.product:
            _enrich(resp, item.product)
        results.append(resp)
    return results


@router.post(
    "/garage",
    response_model=GarageItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_to_garage(
    payload: GarageItemCreate,
    session: Session = Depends(get_session),  # noqa: B008
) -> GarageItemResponse:
    product = session.query(Product).filter(Product.id == payload.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    item = GarageItem(
        product_id=payload.product_id,
        status="planejando",
        saved_at=datetime.now(tz=UTC),
    )
    session.add(item)
    try:
        session.commit()
        session.refresh(item)
    except IntegrityError:
        session.rollback()
        existing = (
            session.query(GarageItem)
            .filter(GarageItem.product_id == payload.product_id)
            .first()
        )
        if existing:
            item = existing
        else:
            raise HTTPException(
                status_code=400, detail="Could not add to garage"
            ) from None

    resp = GarageItemResponse.model_validate(item)
    return _enrich(resp, product)


@router.put("/garage/{product_id}/status", response_model=GarageItemResponse)
def update_garage_item_status(
    product_id: str,
    payload: GarageItemUpdateStatus,
    session: Session = Depends(get_session),  # noqa: B008
) -> GarageItemResponse:
    item = session.query(GarageItem).filter(GarageItem.product_id == product_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found in garage")

    item.status = payload.status
    session.commit()
    session.refresh(item)

    resp = GarageItemResponse.model_validate(item)
    if item.product:
        _enrich(resp, item.product)
    return resp


@router.delete("/garage/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_garage(
    product_id: str,
    session: Session = Depends(get_session),  # noqa: B008
) -> None:
    item = session.query(GarageItem).filter(GarageItem.product_id == product_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found in garage")

    session.delete(item)
    session.commit()
