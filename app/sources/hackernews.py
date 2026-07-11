"""Hacker News official Firebase API source."""

from __future__ import annotations

import json
from datetime import datetime, timezone

from app.domain.models import IntelligenceItem
from app.infrastructure.http_client import get_text


class HackerNewsSource:
    name = "Hacker News"

    def fetch(self) -> list[IntelligenceItem]:
        identifiers = json.loads(get_text("https://hacker-news.firebaseio.com/v0/topstories.json"))[:15]
        result: list[IntelligenceItem] = []
        for identifier in identifiers:
            story = json.loads(get_text(f"https://hacker-news.firebaseio.com/v0/item/{identifier}.json"))
            if story.get("type") != "story" or not story.get("title"):
                continue
            result.append(IntelligenceItem(story["title"], story.get("url", f"https://news.ycombinator.com/item?id={identifier}"), self.name, datetime.fromtimestamp(story.get("time", 0), timezone.utc), "Developer community discussion.", int(story.get("score", 0)), "科技"))
        return result
