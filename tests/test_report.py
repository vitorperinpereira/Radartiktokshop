from __future__ import annotations

import builtins
import csv
import json
from pathlib import Path
from uuid import uuid4

import pytest

from ranking import RankingService, from_json, to_csv, to_json
from ranking.cli import _print_console_line, main
from scoring import ProductSignals


def _sample_products() -> list[ProductSignals]:
    return [
        ProductSignals(
            product_id="product-1",
            name="Heatless Curling Ribbon",
            category="beauty",
            price=20.0,
            commission_rate=0.12,
            sales_velocity=30.0,
            view_growth_7d=10.0,
            view_growth_3d=15.0,
            active_creators=20,
            days_since_detected=2,
            demo_value=88.0,
            visual_transform=90.0,
            hook_clarity=80.0,
        ),
        ProductSignals(
            product_id="product-2",
            name="Portable Blender Cup",
            category="fitness",
            price=35.0,
            commission_rate=0.08,
            sales_velocity=18.0,
            view_growth_7d=7.0,
            view_growth_3d=6.0,
            active_creators=40,
            days_since_detected=6,
            demo_value=70.0,
            visual_transform=65.0,
            hook_clarity=72.0,
        ),
    ]


def _unique_output_path(suffix: str) -> Path:
    return Path(f".tmp/ranking-test-{uuid4()}{suffix}")


def test_to_json_creates_file() -> None:
    report = RankingService().generate_ranking(_sample_products(), top_n=2)
    output_path = _unique_output_path(".json")

    try:
        to_json(report, str(output_path))

        assert output_path.exists()
        payload = json.loads(output_path.read_text(encoding="utf-8"))
        assert payload["report_id"] == report.report_id
        assert len(payload["entries"]) == 2
    finally:
        output_path.unlink(missing_ok=True)


def test_to_csv_creates_file() -> None:
    report = RankingService().generate_ranking(_sample_products(), top_n=2)
    output_path = _unique_output_path(".csv")

    try:
        to_csv(report, str(output_path))

        assert output_path.exists()
        with output_path.open("r", encoding="utf-8", newline="") as csv_file:
            rows = list(csv.reader(csv_file))

        assert len(rows[0]) == 13
        assert rows[0][0] == "rank"
    finally:
        output_path.unlink(missing_ok=True)


def test_from_json_roundtrip() -> None:
    report = RankingService().generate_ranking(_sample_products(), top_n=2)
    output_path = _unique_output_path(".json")

    try:
        to_json(report, str(output_path))
        loaded = from_json(str(output_path))

        assert loaded.model_dump() == report.model_dump()
    finally:
        output_path.unlink(missing_ok=True)


def test_csv_row_count_matches_entries() -> None:
    report = RankingService().generate_ranking(_sample_products(), top_n=2)
    output_path = _unique_output_path(".csv")

    try:
        to_csv(report, str(output_path))
        with output_path.open("r", encoding="utf-8", newline="") as csv_file:
            rows = list(csv.reader(csv_file))

        assert len(rows) == len(report.entries) + 1
    finally:
        output_path.unlink(missing_ok=True)


def test_cli_main_generates_outputs_and_prints_summary(capsys: pytest.CaptureFixture[str]) -> None:
    input_path = _unique_output_path(".json")
    output_dir = Path(f".tmp/ranking-cli-{uuid4()}")

    try:
        input_path.parent.mkdir(parents=True, exist_ok=True)
        input_path.write_text(
            json.dumps([product.model_dump(mode="json") for product in _sample_products()]),
            encoding="utf-8",
        )

        exit_code = main(
            [
                "--input",
                str(input_path),
                "--top",
                "2",
                "--min-score",
                "0",
                "--output-dir",
                str(output_dir),
            ]
        )

        captured = capsys.readouterr()
        assert exit_code == 0
        assert "Ranking gerado:" in captured.out
        assert "Top 3:" in captured.out
        assert list(output_dir.glob("ranking_*.json"))
        assert list(output_dir.glob("ranking_*.csv"))
    finally:
        for report_path in output_dir.glob("*"):
            report_path.unlink(missing_ok=True)
        output_dir.rmdir()
        input_path.unlink(missing_ok=True)


def test_print_console_line_falls_back_when_stdout_cannot_encode_unicode(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    written_messages: list[str] = []

    def fake_print(message: str) -> None:
        if any(ord(character) > 255 for character in message):
            raise UnicodeEncodeError("charmap", message, 0, 1, "character maps to <undefined>")
        written_messages.append(message)

    monkeypatch.setattr(builtins, "print", fake_print)

    _print_console_line(
        "\U0001f4c1 Arquivos salvos em: outputs",
        fallback="Arquivos salvos em: outputs",
    )

    assert written_messages == ["Arquivos salvos em: outputs"]
