"""Dcard's public popular-post feed for Taiwan youth discussion signals."""

from __future__ import annotations

from datetime import datetime, timezone

from app.domain.models import IntelligenceItem
from app.infrastructure.http_client import get_text


class DcardSource:
    name = "Dcard"

    def fetch(self) -> list[IntelligenceItem]:
        import json

        posts = json.loads(get_text("https://www.dcard.tw/service/api/v2/posts?popular=true&limit=60"))
        result: list[IntelligenceItem] = []
        for post in posts:
            title = str(post.get("title") or "").strip()
            if not title:
                continue
            excerpt = str(post.get("excerpt") or "")
            category = self._category(str(post.get("forumName") or ""), title, excerpt)
            engagement = int(post.get("likeCount") or 0) + int(post.get("commentCount") or 0) * 3
            result.append(IntelligenceItem(title, f"https://www.dcard.tw/f/{post.get('forumAlias', '')}/p/{post.get('id', '')}", self.name, datetime.fromisoformat(str(post.get("createdAt")).replace("Z", "+00:00")) if post.get("createdAt") else datetime.now(timezone.utc), excerpt, engagement, category))
        return result

    @staticmethod
    def _category(forum: str, title: str = "", excerpt: str = "") -> str:
        text = f"{forum} {title} {excerpt}"
        if "台中" in text and any(keyword in text for keyword in ("美食", "餐廳", "活動", "展覽", "優惠", "兌換", "景點", "一中")):
            return "台中好康與活動"
        mapping = {
            "遊戲": "遊戲與電競",
            "動漫": "動漫與娛樂",
            "追星": "動漫與娛樂",
            "美食": "生活流行",
            "旅遊": "生活流行",
            "穿搭": "生活流行",
            "彩妝": "生活流行",
            "感情": "生活流行",
            "閒聊": "生活流行",
            "有趣": "生活流行",
            "女孩": "生活流行",
            "梗圖": "生活流行",
            "心情": "生活流行",
            "寵物": "生活流行",
            "居家": "生活流行",
            "汽機車": "生活流行",
            "工作": "生活流行",
        }
        return next((category for keyword, category in mapping.items() if keyword in forum), "生活流行")
