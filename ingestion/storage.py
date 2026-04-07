"""Local JSON cache for raw ingestion payloads and synthesized ProductSignals."""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from scoring import ProductSignals


def _slugify(value: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9]+", "-", value.strip().lower()).strip("-")
    return normalized or "keyword"


class IngestionCache:
    """File-backed JSON cache for raw source payloads and synthesized signals."""

    def __init__(self, cache_dir: str = ".cache/ingestion") -> None:
        self.cache_dir = Path(cache_dir)

    def save_raw(self, keyword: str, source: str, data: list[dict[str, Any]]) -> None:
        """Persist one raw source payload under the source/keyword/date cache path."""

        target_dir = self.cache_dir / source
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / f"{_slugify(keyword)}_{datetime.now(UTC):%Y-%m-%d}.json"
        target_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def load_raw(
        self,
        keyword: str,
        source: str,
        date: str | None = None,
    ) -> list[dict[str, Any]] | None:
        """Load the latest raw source payload for one keyword/source pair."""

        source_dir = self.cache_dir / source
        if not source_dir.exists():
            return None

        if date is not None:
            target_path = source_dir / f"{_slugify(keyword)}_{date}.json"
            if not target_path.exists():
                return None
            payload = json.loads(target_path.read_text(encoding="utf-8"))
            return payload if isinstance(payload, list) else None

        candidates = sorted(source_dir.glob(f"{_slugify(keyword)}_*.json"))
        if not candidates:
            return None
        payload = json.loads(candidates[-1].read_text(encoding="utf-8"))
        return payload if isinstance(payload, list) else None

    def save_signals(self, signals: list[ProductSignals]) -> None:
        """Persist one synthesized ProductSignals batch into the local cache."""

        signals_dir = self.cache_dir / "signals"
        signals_dir.mkdir(parents=True, exist_ok=True)
        target_path = signals_dir / f"signals_{datetime.now(UTC):%Y%m%dT%H%M%SZ}.json"
        target_path.write_text(
            json.dumps([signal.model_dump(mode="json") for signal in signals], indent=2),
            encoding="utf-8",
        )

    def load_latest_signals(self) -> list[ProductSignals] | None:
        """Load the latest globally cached ProductSignals batch."""

        signals_dir = self.cache_dir / "signals"
        if not signals_dir.exists():
            return None

        candidates = sorted(signals_dir.glob("signals_*.json"))
        if not candidates:
            return None

        payload = json.loads(candidates[-1].read_text(encoding="utf-8"))
        if not isinstance(payload, list):
            return None
        return [ProductSignals.model_validate(item) for item in payload]
