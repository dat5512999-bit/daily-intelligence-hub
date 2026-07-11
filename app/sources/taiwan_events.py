"""Official Taiwan Tourism events: a stable, no-login lifestyle signal."""

from __future__ import annotations

from datetime import datetime, timezone
from html import unescape
from html.parser import HTMLParser
from urllib.parse import urljoin

from app.domain.models import IntelligenceItem
from app.infrastructure.http_client import get_text


class _EventLinkParser(HTMLParser):
    """Extract candidate event links from the Tourism Administration listing."""

    def __init__(self) -> None:
        super().__init__()
        self._href = ""
        self._parts: list[str] = []
        self.links: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            self._href = dict(attrs).get("href") or ""
            self._parts = []

    def handle_data(self, data: str) -> None:
        if self._href:
            self._parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._href:
            title = " ".join(" ".join(self._parts).split())
            self.links.append((self._href, unescape(title)))
            self._href = ""
            self._parts = []


class TaiwanTourismEventsSource:
    """Use a government event listing instead of depending on a social platform."""

    name = "觀光署活動"
    _url = "https://www.taiwan.net.tw/m1.aspx?sNo=0001019"
    _event_words = ("活動", "展", "節", "市集", "音樂", "演唱", "旅遊", "美食", "文化", "嘉年華", "夏日", "藝術", "燈會")

    def fetch(self) -> list[IntelligenceItem]:
        parser = _EventLinkParser()
        parser.feed(get_text(self._url))
        result: list[IntelligenceItem] = []
        seen: set[str] = set()
        for href, title in parser.links:
            if not title or title in seen or not any(word in title for word in self._event_words):
                continue
            # Navigation links are much shorter and do not identify a specific event.
            if len(title) < 8:
                continue
            seen.add(title)
            category = "台中好康與活動" if "台中" in title else "生活流行"
            result.append(IntelligenceItem(
                title=title,
                url=urljoin(self._url, href),
                source=self.name,
                published_at=datetime.now(timezone.utc),
                summary="交通部觀光署公開活動資訊；適合查看展覽、旅遊、美食、市集或限時行程，出發前請再開啟官方頁確認日期。",
                engagement=180,
                category=category,
            ))
            if len(result) >= 12:
                break
        if not result:
            raise RuntimeError("觀光署活動頁暫時沒有可讀取的生活活動資料。")
        return result
