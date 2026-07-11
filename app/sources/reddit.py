"""Public Reddit RSS source; no account or private data required."""

from __future__ import annotations

import xml.etree.ElementTree as element_tree
from datetime import datetime

from app.domain.models import IntelligenceItem
from app.infrastructure.http_client import get_text
from app.sources.base import utc_now


class RedditSource:
    name = "Reddit"
    _feeds = (
        ("https://www.reddit.com/r/technology/.rss", "科技"),
        ("https://www.reddit.com/r/artificial/.rss", "AI"),
        ("https://www.reddit.com/r/travel/.rss", "旅遊生活"),
        ("https://www.reddit.com/r/food/.rss", "美食生活"),
        ("https://www.reddit.com/r/health/.rss", "健康生活"),
        ("https://www.reddit.com/r/movies/.rss", "娛樂文化"),
    )

    def fetch(self) -> list[IntelligenceItem]:
        items: list[IntelligenceItem] = []
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        for feed, category in self._feeds:
            root = element_tree.fromstring(get_text(feed))
            for entry in root.findall("atom:entry", ns)[:6]:
                link = entry.find("atom:link", ns)
                published = entry.findtext("atom:published", default="", namespaces=ns)
                timestamp = datetime.fromisoformat(published.replace("Z", "+00:00")) if published else utc_now()
                items.append(IntelligenceItem(entry.findtext("atom:title", default="未命名貼文", namespaces=ns), link.attrib.get("href", "") if link is not None else "", self.name, timestamp, entry.findtext("atom:content", default="", namespaces=ns), 0, category))
        if not items:
            raise RuntimeError("No RSS entries returned.")
        return items
