"""Quality filters for raw source items."""

from __future__ import annotations

import re

from app.domain.models import IntelligenceItem

LOW_CONTEXT_TITLES = {"meet", "fff", "#fff", "google meet"}
LOW_CONTEXT_PATTERNS = (
    re.compile(r"^tiktok 熱門標籤：#[a-z]{2,4}$", re.IGNORECASE),
    re.compile(r"^tiktok 熱門標籤：#[\w]*_[\w_]*$", re.IGNORECASE),
    re.compile(r"^tiktok 熱門標籤：#[a-f0-9]{5,}$", re.IGNORECASE),
    re.compile(r"^tiktok 熱門標籤：#[a-z0-9]*\d[a-z0-9]*$", re.IGNORECASE),
    re.compile(r"^[a-z]{2,5}$", re.IGNORECASE),
)


def _has_low_context(item: IntelligenceItem) -> bool:
    normalized = item.title.strip().lower()
    if normalized in LOW_CONTEXT_TITLES:
        return True
    if item.source in {"Google 熱門搜尋", "TikTok"}:
        return any(pattern.search(normalized) for pattern in LOW_CONTEXT_PATTERNS)
    return False


def filter_items(items: list[IntelligenceItem]) -> list[IntelligenceItem]:
    """Remove malformed and repeated source records while preserving source diversity."""
    seen: set[tuple[str, str]] = set()
    result: list[IntelligenceItem] = []
    for item in items:
        key = (item.source, item.url)
        if not item.title.strip() or not item.url.startswith("http") or key in seen or _has_low_context(item):
            continue
        seen.add(key)
        result.append(item)
    return result
