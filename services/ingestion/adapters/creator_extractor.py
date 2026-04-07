"""Creator extraction helpers for Apify-style video payloads."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from services.shared.db.models import Creator, CreatorProduct


def _coerce_text(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, dict):
        for key in ("name", "username", "handle", "id"):
            nested = _coerce_text(value.get(key))
            if nested is not None:
                return nested
        return None
    text = str(value).strip().lstrip("@")
    return text or None


def _coerce_int(value: object) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _extract_author(payload: dict[str, Any]) -> dict[str, Any] | None:
    author = payload.get("author")
    if isinstance(author, dict):
        return author

    author_meta = payload.get("authorMeta")
    if isinstance(author_meta, dict):
        return author_meta

    return None


def _infer_niche(payload: dict[str, Any]) -> str | None:
    for key in ("niche", "category", "subcategory", "topic"):
        value = _coerce_text(payload.get(key))
        if value is not None:
            return value

    desc = _coerce_text(payload.get("desc"))
    if desc is None:
        return None

    tokens = [token for token in desc.lower().replace("#", " ").split() if token]
    for token in tokens:
        if len(token) >= 4:
            return token
    return None


def extract_creators_from_video_payload(raw_payload: dict[str, Any]) -> list[dict[str, object]]:
    """Extract a single creator record from a raw TikTok video payload."""

    if not isinstance(raw_payload, dict):
        return []

    author = _extract_author(raw_payload)
    if author is None:
        return []

    handle = _coerce_text(
        author.get("uniqueId") or author.get("nickname") or author.get("name") or author.get("id")
    )
    if handle is None:
        return []

    follower_count = _coerce_int(
        author.get("followerCount")
        or author.get("followers")
        or author.get("fans")
        or author.get("follower_count")
    )

    region = _coerce_text(
        author.get("region") or author.get("countryCode") or raw_payload.get("region")
    )
    niche = _infer_niche(raw_payload)

    return [
        {
            "handle": handle,
            "follower_count": follower_count,
            "niche": niche,
            "region": region,
            "source_video_id": _coerce_text(raw_payload.get("id")),
            "raw_payload": raw_payload,
        }
    ]


def _upsert_creator(session: Session, creator_data: dict[str, object]) -> Creator:
    handle = str(creator_data["handle"])
    existing = session.execute(select(Creator).where(Creator.handle == handle)).scalar_one_or_none()
    if existing is not None:
        existing.primary_niche = (
            str(creator_data["niche"]) if creator_data.get("niche") else existing.primary_niche
        )
        existing.region = (
            str(creator_data["region"]) if creator_data.get("region") else existing.region
        )
        return existing

    creator = Creator(
        handle=handle,
        tier=None,
        primary_niche=str(creator_data["niche"]) if creator_data.get("niche") else None,
        region=str(creator_data["region"]) if creator_data.get("region") else None,
        created_at=datetime.now(UTC),
    )
    session.add(creator)
    session.flush()
    return creator


def persist_creators(
    session: Session,
    creators: list[dict[str, object]],
    *,
    product_id: str,
) -> int:
    """Persist creator records and link them to one product."""

    created_links = 0
    now = datetime.now(UTC)
    for creator_data in creators:
        handle = creator_data.get("handle")
        if not isinstance(handle, str) or not handle.strip():
            continue

        creator = _upsert_creator(session, creator_data)
        existing_link = session.execute(
            select(CreatorProduct).where(
                CreatorProduct.creator_id == creator.id,
                CreatorProduct.product_id == product_id,
            )
        ).scalar_one_or_none()
        if existing_link is None:
            session.add(
                CreatorProduct(
                    creator_id=creator.id,
                    product_id=product_id,
                    first_seen_at=now,
                    last_seen_at=now,
                    created_at=now,
                )
            )
            created_links += 1
            continue

        existing_link.last_seen_at = now

    return created_links
