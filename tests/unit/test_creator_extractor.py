from __future__ import annotations

from uuid import uuid4

from sqlalchemy import select

from services.ingestion.adapters.creator_extractor import (
    extract_creators_from_video_payload,
    persist_creators,
)
from services.shared.config import ROOT_DIR, AppSettings
from services.shared.db import Base, Creator, CreatorProduct, Product
from services.shared.db.session import build_engine, build_session_factory


def test_extract_creators_from_video_payload_reads_expected_fields() -> None:
    payload = {
        "id": "video-1",
        "desc": "review do mini massager #beauty #relax",
        "author": {
            "id": "123",
            "uniqueId": "@creatorbr",
            "followerCount": 1200,
            "region": "BR",
        },
    }

    creators = extract_creators_from_video_payload(payload)

    assert len(creators) == 1
    assert creators[0]["handle"] == "creatorbr"
    assert creators[0]["follower_count"] == 1200
    assert creators[0]["niche"] == "review"
    assert creators[0]["region"] == "BR"


def test_persist_creators_upserts_creator_and_pivot() -> None:
    temp_dir = ROOT_DIR / ".tmp"
    temp_dir.mkdir(exist_ok=True)
    db_path = temp_dir / f"creator-extractor-{uuid4().hex}.sqlite3"
    settings = AppSettings(database_url=f"sqlite+pysqlite:///{db_path.as_posix()}")

    engine = build_engine(settings=settings)
    Base.metadata.create_all(engine)
    session_factory = build_session_factory(settings=settings)

    with session_factory() as session:
        product = Product(
            id="product-1",
            canonical_key="demo::product",
            title="Mini Massager",
            brand=None,
            category="Beauty",
            subcategory=None,
            image_url=None,
            status="active",
        )
        session.add(product)
        session.flush()

        created = persist_creators(
            session,
            [
                {
                    "handle": "creatorbr",
                    "follower_count": 1200,
                    "niche": "beauty",
                    "region": "BR",
                }
            ],
            product_id=product.id,
        )
        session.commit()

    assert created == 1

    with session_factory() as session:
        creators = session.scalars(select(Creator)).all()
        links = session.scalars(select(CreatorProduct)).all()

    assert len(creators) == 1
    assert creators[0].handle == "creatorbr"
    assert len(links) == 1
    assert links[0].product_id == "product-1"
