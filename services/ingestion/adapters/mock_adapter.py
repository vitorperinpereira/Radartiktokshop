"""Mock ingestion adapter for local bootstrapping."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any

from services.ingestion.contracts import IngestionRecord

SeedRow = dict[str, Any]

_SEED_PROFILES: dict[str, list[SeedRow]] = {
    "smoke": [
        {
            "title": "Portable Blender Cup",
            "brand": "BlendGo",
            "category": "Kitchen",
            "subcategory": "Drinkware",
            "image_url": "https://example.com/blender-cup.jpg",
            "price": Decimal("29.90"),
            "orders_estimate": 180,
            "rating": Decimal("4.70"),
            "commission_rate": Decimal("12.50"),
            "country": "BR",
        },
        {
            "title": "Heatless Curling Ribbon",
            "brand": "Veloura",
            "category": "Beauty",
            "subcategory": "Haircare",
            "image_url": "https://example.com/curling-ribbon.jpg",
            "price": Decimal("14.90"),
            "orders_estimate": 320,
            "rating": Decimal("4.80"),
            "commission_rate": Decimal("18.00"),
            "country": "BR",
        },
        {
            "title": "Pet Hair Roller",
            "brand": "LintEase",
            "category": "Home",
            "subcategory": "Cleaning",
            "image_url": "https://example.com/pet-hair-roller.jpg",
            "price": Decimal("11.50"),
            "orders_estimate": 410,
            "rating": Decimal("4.60"),
            "commission_rate": Decimal("10.00"),
            "country": "BR",
        },
    ],
    "demo_weekly": [
        {
            "title": "Portable Blender Cup",
            "brand": "BlendGo",
            "category": "Kitchen",
            "subcategory": "Drinkware",
            "image_url": "https://example.com/blender-cup.jpg",
            "price": Decimal("29.90"),
            "orders_estimate": 180,
            "rating": Decimal("4.70"),
            "commission_rate": Decimal("12.50"),
            "country": "BR",
        },
        {
            "title": "Heatless Curling Ribbon",
            "brand": "Veloura",
            "category": "Beauty",
            "subcategory": "Haircare",
            "image_url": "https://example.com/curling-ribbon.jpg",
            "price": Decimal("14.90"),
            "orders_estimate": 320,
            "rating": Decimal("4.80"),
            "commission_rate": Decimal("18.00"),
            "country": "BR",
        },
        {
            "title": "Pet Hair Roller",
            "brand": "LintEase",
            "category": "Home",
            "subcategory": "Cleaning",
            "image_url": "https://example.com/pet-hair-roller.jpg",
            "price": Decimal("11.50"),
            "orders_estimate": 410,
            "rating": Decimal("4.60"),
            "commission_rate": Decimal("10.00"),
            "country": "BR",
        },
        {
            "title": "Mini Seal Vacuum",
            "brand": "FreshLock",
            "category": "Kitchen",
            "subcategory": "Storage",
            "image_url": "https://example.com/mini-sealer.jpg",
            "price": Decimal("24.50"),
            "orders_estimate": 265,
            "rating": Decimal("4.50"),
            "commission_rate": Decimal("15.25"),
            "country": "BR",
        },
        {
            "title": "LED Sunset Lamp",
            "brand": "GlowNest",
            "category": "Home",
            "subcategory": "Decor",
            "image_url": "https://example.com/sunset-lamp.jpg",
            "price": Decimal("21.90"),
            "orders_estimate": 510,
            "rating": Decimal("4.90"),
            "commission_rate": Decimal("16.75"),
            "country": "BR",
        },
    ],
    "edge_cases": [
        {
            # Gate: orders_estimate=0 — should be skipped (no sales)
            "title": "Portable Blender Cup",
            "brand": None,
            "category": "Kitchen",
            "subcategory": None,
            "image_url": None,
            "price": Decimal("29.90"),
            "orders_estimate": 0,
            "rating": None,
            "commission_rate": Decimal("12.50"),
            "country": "BR",
        },
        {
            # Gate: commission_rate=None — should be skipped (no commission)
            "title": "Portable   Blender Cup!!!",
            "brand": "BlendGo",
            "category": None,
            "subcategory": "Drinkware",
            "image_url": "https://example.com/blender-cup-2.jpg",
            "price": Decimal("28.90"),
            "orders_estimate": 35,
            "rating": Decimal("4.10"),
            "commission_rate": None,
            "country": "BR",
        },
        {
            # Gate: non-BR country — should be skipped
            "title": "Global Organizer Bin",
            "brand": "OrgGlobal",
            "category": "Home",
            "subcategory": "Storage",
            "image_url": "https://example.com/organizer.jpg",
            "price": Decimal("19.90"),
            "orders_estimate": 120,
            "rating": Decimal("4.30"),
            "commission_rate": Decimal("8.00"),
            "country": "US",
        },
        {
            # Valid: should pass all gates
            "title": "Silicone Kitchen Spatula Set",
            "brand": "CookBR",
            "category": "Kitchen",
            "subcategory": "Utensils",
            "image_url": "https://example.com/spatula.jpg",
            "price": Decimal("18.90"),
            "orders_estimate": 95,
            "rating": Decimal("4.50"),
            "commission_rate": Decimal("11.00"),
            "country": "BR",
        },
    ],
}


def load_mock_records(
    *,
    count: int | None = None,
    source_name: str = "mock",
    profile: str = "smoke",
) -> list[IngestionRecord]:
    if profile not in _SEED_PROFILES:
        supported_profiles = ", ".join(sorted(_SEED_PROFILES))
        raise ValueError(
            f"Unsupported mock profile `{profile}`. Expected one of: {supported_profiles}."
        )

    base_time = datetime.now(UTC)
    seed_rows = _SEED_PROFILES[profile]
    target_count = count if count is not None else len(seed_rows)

    records: list[IngestionRecord] = []
    for index in range(target_count):
        template = seed_rows[index % len(seed_rows)]
        source_record_id = f"{profile}-{index + 1}"
        records.append(
            IngestionRecord(
                source_name=source_name,
                input_type="mock",
                title=str(template["title"]),
                brand=str(template["brand"]) if template["brand"] else None,
                category=str(template["category"]) if template["category"] else None,
                subcategory=str(template["subcategory"]) if template["subcategory"] else None,
                image_url=str(template["image_url"]) if template["image_url"] else None,
                source_record_id=source_record_id,
                captured_at=base_time - timedelta(minutes=index * 5),
                price=template["price"],
                orders_estimate=template["orders_estimate"],
                rating=template["rating"],
                commission_rate=template["commission_rate"],
                country=str(template["country"]) if template.get("country") else None,
                raw_payload={
                    **{k: v for k, v in template.items() if k != "country"},
                    "country": template.get("country"),
                    "profile": profile,
                    "source_record_id": source_record_id,
                },
                validation_issues=[],
            )
        )

    return records
