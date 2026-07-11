"""Focused Google News RSS searches generated from the user's interest profile."""

from __future__ import annotations

import xml.etree.ElementTree as element_tree
from email.utils import parsedate_to_datetime
from urllib.parse import quote_plus

from app.domain.models import IntelligenceItem
from app.infrastructure.http_client import get_text
from app.infrastructure.interests import InterestProfile
from app.sources.base import utc_now


class InterestNewsSource:
    name = "Google News"

    def __init__(self, profile: InterestProfile) -> None:
        self._profile = profile

    def fetch(self) -> list[IntelligenceItem]:
        result: list[IntelligenceItem] = []
        for category in self._profile.categories:
            for query in category.queries:
                url = f"https://news.google.com/rss/search?q={quote_plus(query)}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
                root = element_tree.fromstring(get_text(url))
                for item in root.findall("./channel/item")[:8]:
                    title = item.findtext("title", default="未命名新聞")
                    published = item.findtext("pubDate", default="")
                    result.append(IntelligenceItem(title, item.findtext("link", default=""), self.name, parsedate_to_datetime(published) if published else utc_now(), f"這則消息符合你關注的「{category.name}」。開啟原文可確認完整內容與來源。", 0, category.name))
        return result
