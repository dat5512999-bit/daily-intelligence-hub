"""Google Trends Taiwan public RSS feed; measures attention, not truth."""

from __future__ import annotations

import xml.etree.ElementTree as element_tree
from email.utils import parsedate_to_datetime

from app.domain.models import IntelligenceItem
from app.infrastructure.http_client import get_text
from app.sources.base import utc_now


class GoogleTrendsSource:
    name = "Google 熱門搜尋"

    def fetch(self) -> list[IntelligenceItem]:
        root = element_tree.fromstring(get_text("https://trends.google.com/trending/rss?geo=TW"))
        result: list[IntelligenceItem] = []
        for item in root.findall("./channel/item")[:20]:
            title = item.findtext("title", default="未命名搜尋趨勢")
            published = item.findtext("pubDate", default="")
            result.append(IntelligenceItem(title, f"https://trends.google.com/trends/explore?q={title}", self.name, parsedate_to_datetime(published) if published else utc_now(), f"「{title}」最近被更多台灣人搜尋；這只代表大家好奇，不代表網路上的說法已被證實。", 0, "搜尋趨勢"))
        return result
