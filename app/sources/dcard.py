"""Dcard's public popular-post feed for Taiwan youth discussion signals."""

from __future__ import annotations

from datetime import datetime, timezone

from app.domain.models import IntelligenceItem
from app.infrastructure.http_client import get_text


class DcardSource:
    name = "Dcard"

    def fetch(self) -> list[IntelligenceItem]:
        import json

        posts = json.loads(get_text("https://www.dcard.tw/service/api/v2/posts?popular=true&limit=30"))
        result: list[IntelligenceItem] = []
        for post in posts:
            title = str(post.get("title") or "").strip()
            if not title:
                continue
            category = self._category(str(post.get("forumName") or ""))
            engagement = int(post.get("likeCount") or 0) + int(post.get("commentCount") or 0) * 3
            result.append(IntelligenceItem(title, f"https://www.dcard.tw/f/{post.get('forumAlias', '')}/p/{post.get('id', '')}", self.name, datetime.fromisoformat(str(post.get("createdAt")).replace("Z", "+00:00")) if post.get("createdAt") else datetime.now(timezone.utc), str(post.get("excerpt") or ""), engagement, category))
        return result

    @staticmethod
    def _category(forum: str) -> str:
        mapping = {"美食": "美食生活", "旅遊": "旅遊生活", "感情": "生活話題", "穿搭": "生活話題", "彩妝": "生活話題", "追星": "娛樂文化", "閒聊": "生活話題", "工作": "職場生活"}
        return next((category for keyword, category in mapping.items() if keyword in forum), "Dcard 熱門")
