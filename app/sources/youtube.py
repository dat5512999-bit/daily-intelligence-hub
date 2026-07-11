"""Public YouTube channel-update source using Atom feeds.

The source intentionally follows only channels the user chooses. It does not
scrape search results or private data, and requires neither a login nor API key.
"""

from __future__ import annotations

import json
import xml.etree.ElementTree as element_tree
from datetime import datetime
from pathlib import Path

from app.domain.models import IntelligenceItem
from app.infrastructure.http_client import get_text


class YouTubeSource:
    name = "YouTube"
    _config_path = Path("config/youtube_channels.json")

    def fetch(self) -> list[IntelligenceItem]:
        """Fetch recent uploads from channel IDs configured by the user."""
        if not self._config_path.exists():
            return []
        channels = json.loads(self._config_path.read_text(encoding="utf-8"))
        result: list[IntelligenceItem] = []
        namespaces = {"atom": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015"}
        for channel in channels:
            channel_id = channel.get("channel_id", "").strip()
            if not channel_id:
                continue
            root = element_tree.fromstring(get_text(f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"))
            for entry in root.findall("atom:entry", namespaces)[:4]:
                video_id = entry.findtext("yt:videoId", default="", namespaces=namespaces)
                published = entry.findtext("atom:published", default="", namespaces=namespaces)
                result.append(IntelligenceItem(entry.findtext("atom:title", default="未命名影片", namespaces=namespaces), f"https://www.youtube.com/watch?v={video_id}", self.name, datetime.fromisoformat(published.replace("Z", "+00:00")), entry.findtext("atom:content", default="", namespaces=namespaces), 0, channel.get("category", "影音生活"), (channel.get("name", "YouTube 頻道"),)))
        return result
