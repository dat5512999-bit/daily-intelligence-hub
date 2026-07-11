"""Public Reddit RSS source; no account or private data required."""

from __future__ import annotations

import xml.etree.ElementTree as element_tree
from datetime import datetime

from app.domain.models import IntelligenceItem
from app.infrastructure.http_client import clean_xml, get_text
from app.sources.base import utc_now


class RedditSource:
    name = "Reddit"
    _feeds = (
        ("https://www.reddit.com/r/OpenAI/.rss?raw_json=1", "AI／Codex"),
        ("https://www.reddit.com/r/gaming/.rss?raw_json=1", "遊戲與電競"),
        ("https://www.reddit.com/r/Palworld/.rss?raw_json=1", "遊戲與電競"),
        ("https://www.reddit.com/r/anime/.rss?raw_json=1", "動漫與娛樂"),
        ("https://www.reddit.com/r/technology/.rss?raw_json=1", "科技"),
    )

    def fetch(self) -> list[IntelligenceItem]:
        items: list[IntelligenceItem] = []
        failed_feeds = 0
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        for feed, category in self._feeds:
            try:
                root = element_tree.fromstring(clean_xml(get_text(feed, headers={"Referer": "https://www.reddit.com/"})))
            except (OSError, ValueError, element_tree.ParseError):
                # Reddit can rate-limit a shared GitHub Actions IP.  Preserve
                # any other subreddits that did respond instead of failing all.
                failed_feeds += 1
                continue
            for entry in root.findall("atom:entry", ns)[:6]:
                link = entry.find("atom:link", ns)
                published = entry.findtext("atom:published", default="", namespaces=ns)
                timestamp = datetime.fromisoformat(published.replace("Z", "+00:00")) if published else utc_now()
                items.append(IntelligenceItem(entry.findtext("atom:title", default="未命名貼文", namespaces=ns), link.attrib.get("href", "") if link is not None else "", self.name, timestamp, entry.findtext("atom:content", default="", namespaces=ns), 0, category))
        if not items and failed_feeds:
            raise RuntimeError("Reddit 暫時限制自動讀取，已略過；不影響其他來源。")
        return items
