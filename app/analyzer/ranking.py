"""Explainable cross-platform clustering and ranking."""

from __future__ import annotations

import math
import re
from collections import defaultdict
from datetime import datetime, timezone

from app.analyzer.summary import summarize
from app.domain.models import IntelligenceCluster, IntelligenceItem

STOP_WORDS = {"the", "a", "an", "and", "for", "with", "from", "this", "that", "how", "what", "new", "to", "of", "in", "on", "is"}
CATEGORY_BONUS = {"台中現在要注意": 30, "AI／Codex": 25, "遊戲與電競": 20, "動漫與娛樂": 18, "股票與市場": 18, "台中好康與活動": 15}


def _key(title: str) -> frozenset[str]:
    english_words = {word for word in re.findall(r"[a-z0-9]{3,}", title.lower()) if word not in STOP_WORDS}
    chinese_text = "".join(re.findall(r"[\u4e00-\u9fff]+", title))
    chinese_pairs = {chinese_text[index:index + 2] for index in range(max(0, len(chinese_text) - 1))}
    return frozenset(english_words | chinese_pairs)


def _similar(left: frozenset[str], right: frozenset[str]) -> bool:
    return bool(left and right and len(left & right) / len(left | right) >= 0.35)


def rank_items(items: list[IntelligenceItem], limit: int = 10) -> list[IntelligenceCluster]:
    """Merge similar headlines and reward independent source corroboration."""
    groups: list[list[IntelligenceItem]] = []
    keys: list[frozenset[str]] = []
    for item in items:
        item_key = _key(item.title)
        position = next((i for i, key in enumerate(keys) if _similar(key, item_key)), None)
        if position is None:
            groups.append([item]); keys.append(item_key)
        else:
            groups[position].append(item); keys[position] = keys[position] | item_key
    now = datetime.now(timezone.utc)
    clusters: list[IntelligenceCluster] = []
    for group in groups:
        entries = tuple(sorted(group, key=lambda entry: entry.engagement, reverse=True))
        age_hours = max(0.0, (now - max(entry.published_at for entry in entries)).total_seconds() / 3600)
        source_bonus = (len({entry.source for entry in entries}) - 1) * 20
        attention_text = " ".join(entry.title for entry in entries).lower()
        urgent_bonus = 12 if any(word in attention_text for word in ("失火", "火災", "地震", "停電", "事故", "颱風", "淹水", "封路")) else 0
        practical_bonus = 8 if any(word in attention_text for word in ("美股", "台股", "股市", "優惠", "免費", "兌換", "特價", "折扣")) else 0
        score = min(30, math.log1p(sum(max(0, entry.engagement) for entry in entries)) * 5) + max(0, 30 - age_hours / 4) + source_bonus + urgent_bonus + practical_bonus + CATEGORY_BONUS.get(entries[0].category, 0)
        clusters.append(IntelligenceCluster(entries[0].title, entries, entries[0].category, round(score, 1), summarize(entries)))
    return sorted(clusters, key=lambda cluster: cluster.score, reverse=True)[:limit]
