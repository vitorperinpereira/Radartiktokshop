"""Pure video-metrics heuristics for the standalone ingestion pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any


def _nested_value(payload: dict[str, Any], *path: str) -> object:
    current: object = payload
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _as_int(value: object) -> int:
    if isinstance(value, bool):
        return 0
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    return 0


def _clamp_ratio(value: float) -> float:
    return max(0.0, min(1.0, value))


def _coerce_reference_time(videos: list[dict[str, Any]]) -> datetime:
    latest_timestamp = max((_as_int(video.get("createTime")) for video in videos), default=0)
    if latest_timestamp > 0:
        return datetime.fromtimestamp(latest_timestamp, UTC)
    return datetime.fromtimestamp(0, UTC)


def _play_count(video: dict[str, Any]) -> int:
    return _as_int(_nested_value(video, "stats", "playCount") or video.get("playCount"))


def _engagement_count(video: dict[str, Any], field_name: str) -> int:
    return _as_int(_nested_value(video, "stats", field_name) or video.get(field_name))


def _author_id(video: dict[str, Any]) -> str | None:
    author_id = _nested_value(video, "author", "id")
    if author_id in (None, ""):
        author_id = _nested_value(video, "authorMeta", "id")
    if author_id in (None, ""):
        return None
    return str(author_id)


def _recent_play_share(
    videos: list[dict[str, Any]],
    *,
    days: int,
    reference_time: datetime,
) -> float:
    total_play_count = sum(_play_count(video) for video in videos)
    if total_play_count <= 0:
        return 0.0

    cutoff = reference_time - timedelta(days=days)
    recent_play_count = 0
    for video in videos:
        created_at = datetime.fromtimestamp(_as_int(video.get("createTime")), UTC)
        if created_at >= cutoff:
            recent_play_count += _play_count(video)
    return _clamp_ratio(recent_play_count / float(total_play_count))


def _engagement_ratio(videos: list[dict[str, Any]], field_name: str) -> float:
    if not videos:
        return 0.0

    values = [_engagement_count(video, field_name) for video in videos]
    max_value = max(values, default=0)
    if max_value <= 0:
        return 0.0

    average_value = sum(values) / float(len(values))
    return max(0.0, min(100.0, (average_value / float(max_value)) * 100.0))


@dataclass(frozen=True, slots=True)
class VideoMetrics:
    """Keyword-level heuristics extracted from raw TikTok video payloads."""

    view_growth_7d: float
    view_growth_3d: float
    active_creators: int
    demo_value: float
    visual_transform: float
    hook_clarity: float


def compute_video_metrics(videos: list[dict[str, Any]]) -> VideoMetrics:
    """Compute bounded growth and engagement heuristics from raw TikTok videos."""

    if not videos:
        return VideoMetrics(
            view_growth_7d=0.0,
            view_growth_3d=0.0,
            active_creators=0,
            demo_value=0.0,
            visual_transform=0.0,
            hook_clarity=0.0,
        )

    reference_time = _coerce_reference_time(videos)
    author_ids = {
        author_id for video in videos for author_id in [_author_id(video)] if author_id is not None
    }

    return VideoMetrics(
        view_growth_7d=_recent_play_share(videos, days=7, reference_time=reference_time),
        view_growth_3d=_recent_play_share(videos, days=3, reference_time=reference_time),
        active_creators=len(author_ids),
        demo_value=_engagement_ratio(videos, "diggCount"),
        visual_transform=_engagement_ratio(videos, "shareCount"),
        hook_clarity=_engagement_ratio(videos, "commentCount"),
    )
