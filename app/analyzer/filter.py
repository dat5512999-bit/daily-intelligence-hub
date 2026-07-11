"""Quality filters for raw source items."""

from __future__ import annotations

import re
from dataclasses import replace
from html import unescape

from app.domain.models import IntelligenceItem

LOW_CONTEXT_TITLES = {"meet", "fff", "#fff", "google meet"}
LOW_CONTEXT_PATTERNS = (
    re.compile(r"^tiktok 熱門標籤：#[a-z]{2,4}$", re.IGNORECASE),
    re.compile(r"^tiktok 熱門標籤：#[\w]*_[\w_]*$", re.IGNORECASE),
    re.compile(r"^tiktok 熱門標籤：#[a-f0-9]{5,}$", re.IGNORECASE),
    re.compile(r"^tiktok 熱門標籤：#[a-z0-9]*\d[a-z0-9]*$", re.IGNORECASE),
    re.compile(r"^[a-z]{2,5}$", re.IGNORECASE),
)
HTML_TAG = re.compile(r"<[^>]+>")


def _plain_text(value: str) -> str:
    """Keep feed HTML out of a reader-facing report."""
    return " ".join(HTML_TAG.sub(" ", unescape(value)).split())


def _is_unreadable_foreign_post(item: IntelligenceItem) -> bool:
    """This personal Chinese dashboard should not promote untranslated posts.

    English original links remain available through the source, but an all-English
    Reddit/Hacker News title is not useful as a primary daily briefing item.
    """
    if item.source not in {"Reddit", "Hacker News"}:
        return False
    chinese = len(re.findall(r"[\u4e00-\u9fff]", item.title))
    latin = len(re.findall(r"[A-Za-z]", item.title))
    return chinese == 0 and latin >= 18


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
        clean_item = replace(item, title=_plain_text(item.title), summary=_plain_text(item.summary))
        key = (clean_item.source, clean_item.url)
        if (not clean_item.title.strip() or not clean_item.url.startswith("http") or key in seen
                or _has_low_context(clean_item) or _is_unreadable_foreign_post(clean_item)):
            continue
        seen.add(key)
        result.append(clean_item)
    return result
