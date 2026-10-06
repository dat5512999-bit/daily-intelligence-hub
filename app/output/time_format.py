"""Taiwan-first time formatting for reports."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

TAIWAN_TZ = timezone(timedelta(hours=8), "台灣時間")


def format_taiwan_time(value: datetime) -> str:
    """Show report times in the user's local Taiwan timezone."""
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(TAIWAN_TZ).strftime("%Y-%m-%d %H:%M 台灣時間")
