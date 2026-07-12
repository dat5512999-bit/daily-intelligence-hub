"""Focused Google News RSS searches generated from the user's interest profile."""

from __future__ import annotations

import xml.etree.ElementTree as element_tree
from email.utils import parsedate_to_datetime
from urllib.parse import quote_plus

from app.domain.models import IntelligenceItem
from app.infrastructure.http_client import clean_xml, get_text
from app.infrastructure.interests import InterestProfile
from app.sources.base import utc_now


class InterestNewsSource:
    name = "Google News"
    _queries_per_category = 5

    def __init__(self, profile: InterestProfile) -> None:
        self._profile = profile

    def fetch(self) -> list[IntelligenceItem]:
        result: list[IntelligenceItem] = []
        failed_queries = 0
        # Google RSS is public but not an unlimited bulk API.  Rotate a small,
        # relevant slice every hour so all of the user's interests get a turn
        # without making dozens of simultaneous requests from GitHub Actions.
        hour_slot = utc_now().hour
        for category_index, category in enumerate(self._profile.categories):
            queries = self._rotated_queries(category.queries, hour_slot + category_index)
            for query in queries:
                url = f"https://news.google.com/rss/search?q={quote_plus(query)}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
                try:
                    root = element_tree.fromstring(clean_xml(get_text(url)))
                except (OSError, ValueError, element_tree.ParseError):
                    # Keep the news already fetched from other interests.  A
                    # malformed article description must not erase the report.
                    failed_queries += 1
                    continue
                for item in root.findall("./channel/item")[:8]:
                    title = item.findtext("title", default="未命名新聞")
                    published = item.findtext("pubDate", default="")
                    result.append(IntelligenceItem(title, item.findtext("link", default=""), self.name, parsedate_to_datetime(published) if published else utc_now(), f"這則消息符合你關注的「{category.name}」。開啟原文可確認完整內容與來源。", 0, category.name))
        if not result and failed_queries:
            raise RuntimeError("Google News 暫時回傳異常格式，已略過；下次更新會再嘗試。")
        return result

    @classmethod
    def _rotated_queries(cls, queries: tuple[str, ...] | list[str], offset: int) -> list[str]:
        """Return a rotating but topic-spread query window every hour.

        Categories such as games contain several franchises.  Spreading picks
        across the whole list avoids spending one update on five variants of
        the same title (for example, only Palworld).
        """
        if not queries:
            return []
        size = min(cls._queries_per_category, len(queries))
        start = offset % len(queries)
        # Query lists are intentionally interleaved by topic in interests.json,
        # so a rotating consecutive window contains several different subjects.
        return [queries[(start + index) % len(queries)] for index in range(size)]
