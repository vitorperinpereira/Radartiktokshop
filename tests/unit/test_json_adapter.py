import json
from uuid import uuid4

from services.ingestion.adapters.json_adapter import load_json_records
from services.shared.config import ROOT_DIR


def test_json_adapter_returns_typed_records() -> None:
    temp_dir = ROOT_DIR / ".tmp"
    temp_dir.mkdir(exist_ok=True)
    json_path = temp_dir / f"products-{uuid4().hex}.json"
    json_path.write_text(
        json.dumps(
            [
                {
                    "title": "Portable Blender Cup",
                    "brand": "BlendGo",
                    "category": "Kitchen",
                    "subcategory": "Drinkware",
                    "source_record_id": "sku-json-1",
                    "price": "29.90",
                    "orders_estimate": 180,
                    "rating": "4.70",
                    "commission_rate": "12.50",
                    "captured_at": "2026-03-13T10:00:00Z",
                },
                {
                    "title": "   ",
                    "brand": "Veloura",
                    "validation_issues": ["missing_image"],
                },
            ]
        ),
        encoding="utf-8",
    )

    records = load_json_records(json_path)

    assert len(records) == 2
    assert records[0].title == "Portable Blender Cup"
    assert records[0].source_record_id == "sku-json-1"
    assert records[0].raw_payload["brand"] == "BlendGo"
    assert records[1].title == "untitled-record-2"
    assert records[1].source_record_id == f"{json_path.stem}-2"
    assert records[1].validation_issues == ["missing_image", "missing_title"]
