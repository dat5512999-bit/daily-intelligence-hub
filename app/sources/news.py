"""Google News RSS source."""

from __future__ import annotations

import xml.etree.ElementTree as element_tree
from email.utils import parsedate_to_datetime

from app.domain.models import IntelligenceItem
from app.infrastructure.http_client import get_text
from app.sources.base import utc_now


class GoogleNewsSource:
    name = "Google News"

    _topics = (
        ("TECHNOLOGY", "科技"),
        ("BUSINESS", "商業"),
        ("HEALTH", "健康生活"),
        ("ENTERTAINMENT", "娛樂文化"),
        ("WORLD", "全球重要事件"),
        ("NATION", "台灣重要事件"),
    )

    def fetch(self) -> list[IntelligenceItem]:
        result: list[IntelligenceItem] = []
        for topic, category in self._topics:
            url = f"https://news.google.com/rss/headlines/section/topic/{topic}?hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
            root = element_tree.fromstring(get_text(url))
            for item in root.findall("./channel/item")[:5]:
                published = item.findtext("pubDate", default="")
                result.append(IntelligenceItem(item.findtext("title", default="未命名新聞"), item.findtext("link", default=""), self.name, parsedate_to_datetime(published) if published else utc_now(), item.findtext("description", default=""), 0, category))
        return result
