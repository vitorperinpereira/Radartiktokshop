from uuid import uuid4

from services.ingestion.adapters.csv_adapter import load_csv_records
from services.shared.config import ROOT_DIR


def test_csv_adapter_returns_typed_records() -> None:
    temp_dir = ROOT_DIR / ".tmp"
    temp_dir.mkdir(exist_ok=True)
    csv_path = temp_dir / f"products-{uuid4().hex}.csv"
    csv_path.write_text(
        (
            "title,brand,category,subcategory,source_record_id,price,orders_estimate,rating,commission_rate\n"
            "Portable Blender Cup,BlendGo,Kitchen,Drinkware,sku-1,29.90,180,4.70,12.50\n"
        ),
        encoding="utf-8",
    )

    records = load_csv_records(csv_path)

    assert len(records) == 1
    assert records[0].title == "Portable Blender Cup"
    assert records[0].source_record_id == "sku-1"
    assert records[0].raw_payload["brand"] == "BlendGo"
