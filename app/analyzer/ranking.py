"""Explainable cross-platform clustering and ranking."""

from __future__ import annotations

import math
import re
from collections import defaultdict
from datetime import datetime, timezone

from app.analyzer.summary import summarize
from app.domain.models import IntelligenceCluster, IntelligenceItem

STOP_WORDS = {"the", "a", "an", "and", "for", "with", "from", "this", "that", "how", "what", "new", "to", "of", "in", "on", "is"}
CATEGORY_BONUS = {
    "台中現在要注意": 30,
    "年輕人流行": 27,
    "AI／Codex": 26,
    "運動焦點": 25,
    "生活流行": 24,
    "社群冷門雷達": 23,
    "搜尋趨勢": 22,
    "短影音趨勢": 21,
    "遊戲與電競": 20,
    "動漫與娛樂": 19,
    "股票與市場": 18,
    "台中好康與活動": 17,
    "GitHub": 16,
}
CATEGORY_LIMIT = 3
GAME_FAMILIES = {
    "palworld": ("幻獸帕魯", "palworld", "帕魯", "pocketpair"),
    "gta": ("gta", "grand theft auto"),
    "sf": ("sf online", "special force"),
    "forza": ("地平線", "forza"),
    "warcraft": ("魔獸", "warcraft", "寒冰霸權", "寒冰爭霸"),
}


def _key(title: str) -> frozenset[str]:
    # The shared display prefix must not merge every Trending repository into
    # one cluster.  The repository name itself is the meaningful topic.
    title = re.sub(r"^GitHub 今日熱門專案[：:]\s*", "", title, flags=re.IGNORECASE)
    english_words = {word for word in re.findall(r"[a-z0-9]{3,}", title.lower()) if word not in STOP_WORDS}
    chinese_text = "".join(re.findall(r"[\u4e00-\u9fff]+", title))
    chinese_pairs = {chinese_text[index:index + 2] for index in range(max(0, len(chinese_text) - 1))}
    return frozenset(english_words | chinese_pairs)


def _similar(left: frozenset[str], right: frozenset[str]) -> bool:
    return bool(left and right and len(left & right) / len(left | right) >= 0.35)


def rank_items(items: list[IntelligenceItem], limit: int = 24) -> list[IntelligenceCluster]:
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
        practical_bonus = 8 if any(word in attention_text for word in ("美股", "台股", "股市", "優惠", "免費", "兌換", "特價", "折扣", "餐廳", "展覽", "活動")) else 0
        score = min(30, math.log1p(sum(max(0, entry.engagement) for entry in entries)) * 5) + max(0, 30 - age_hours / 4) + source_bonus + urgent_bonus + practical_bonus + CATEGORY_BONUS.get(entries[0].category, 0)
        clusters.append(IntelligenceCluster(entries[0].title, entries, entries[0].category, round(score, 1), summarize(entries)))
    return _balance_categories(sorted(clusters, key=lambda cluster: cluster.score, reverse=True), limit)


def _balance_categories(clusters: list[IntelligenceCluster], limit: int) -> list[IntelligenceCluster]:
    """Fill the first, second and third slot of every category in rounds.

    The previous implementation guaranteed only one item per category, then let
    globally high-scoring categories consume the remaining capacity.  A round-
    robin pass makes the three-item UI promise real whenever a source supplied
    three distinct candidates.
    """
    selected: list[IntelligenceCluster] = []
    used_titles: set[str] = set()
    category_counts: defaultdict[str, int] = defaultdict(int)
    used_families: defaultdict[str, set[str]] = defaultdict(set)
    categories = sorted({cluster.category for cluster in clusters}, key=lambda category: CATEGORY_BONUS.get(category, 0), reverse=True)

    for _round in range(CATEGORY_LIMIT):
        for category in categories:
            if len(selected) >= limit:
                return selected
            candidates = [cluster for cluster in clusters if cluster.category == category and cluster.title not in used_titles]
            candidate = next(
                (cluster for cluster in candidates if _topic_family(cluster) not in used_families[category]),
                candidates[0] if candidates else None,
            )
            if candidate is None:
                continue
            selected.append(candidate)
            used_titles.add(candidate.title)
            category_counts[candidate.category] += 1
            used_families[category].add(_topic_family(candidate))

    return selected


def _topic_family(cluster: IntelligenceCluster) -> str:
    """Keep three slots from becoming three articles about one game."""
    lowered = cluster.title.lower()
    if cluster.category == "遊戲與電競":
        for family, terms in GAME_FAMILIES.items():
            if any(term in lowered for term in terms):
                return family
    return lowered
