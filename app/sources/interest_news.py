"""Focused Google News RSS searches generated from the user's interest profile."""

from __future__ import annotations

import xml.etree.ElementTree as element_tree
import re
from datetime import datetime, timedelta, timezone
from html import unescape
from email.utils import parsedate_to_datetime
from urllib.parse import quote_plus, urlparse

from app.domain.models import IntelligenceItem
from app.infrastructure.http_client import clean_xml, get_text
from app.infrastructure.interests import InterestProfile
from app.sources.base import utc_now


class InterestNewsSource:
    name = "Google News"
    _queries_per_category = 5
    _taiwan_timezone = timezone(timedelta(hours=8))

    def __init__(self, profile: InterestProfile) -> None:
        self._profile = profile

    def fetch(self) -> list[IntelligenceItem]:
        result: list[IntelligenceItem] = []
        failed_queries = 0
        # Google RSS is public but not an unlimited bulk API.  Rotate a small,
        # relevant slice every hour so all of the user's interests get a turn
        # without making dozens of simultaneous requests from GitHub Actions.
        hour_slot = utc_now().hour
        for category_index, category in enumerate(self._profile.categories):
            resolved = self._resolve_queries(category.queries, datetime.now(self._taiwan_timezone))
            queries = self._rotated_queries(resolved, hour_slot + category_index)
            for query in queries:
                url = f"https://news.google.com/rss/search?q={quote_plus(query)}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
                try:
                    root = element_tree.fromstring(clean_xml(get_text(url)))
                except (OSError, ValueError, element_tree.ParseError):
                    # Keep the news already fetched from other interests.  A
                    # malformed article description must not erase the report.
                    failed_queries += 1
                    continue
                for item in root.findall("./channel/item")[:8]:
                    title = item.findtext("title", default="未命名新聞")
                    published = item.findtext("pubDate", default="")
                    # News RSS descriptions often contain only linked headlines.
                    # Preserve an actual excerpt only when it differs from the title.
                    description = " ".join(re.sub(r"<[^>]+>", " ", unescape(item.findtext("description", default=""))).split())
                    headline = title.rsplit(" - ", 1)[0].strip()
                    if headline in description or len(description) < 25:
                        description = ""
                    result.append(IntelligenceItem(
                        title,
                        item.findtext("link", default=""),
                        self.name,
                        parsedate_to_datetime(published) if published else utc_now(),
                        description,
                        0,
                        category.name,
                        image_url=self._feed_image(item),
                    ))
        if not result and failed_queries:
            raise RuntimeError("Google News 暫時回傳異常格式，已略過；下次更新會再嘗試。")
        return result

    @staticmethod
    def _feed_image(item: element_tree.Element) -> str:
        """Read an image explicitly attached to an RSS item; never guess a URL.

        Google News may include media:content, media:thumbnail, or an image
        enclosure. Only HTTPS URLs with a hostname are accepted. This is a
        best-effort preview, not a promise that a publisher keeps it available.
        """
        for element in item.iter():
            if element.tag.rsplit("}", 1)[-1] not in {"content", "thumbnail", "enclosure"}:
                continue
            if element.get("medium") not in (None, "image"):
                continue
            mime_type = element.get("type", "").lower()
            if mime_type and not mime_type.startswith("image/"):
                continue
            candidate = element.get("url", "").strip()
            parsed = urlparse(candidate)
            if parsed.scheme == "https" and parsed.hostname and not parsed.username and not parsed.password:
                return candidate
        return ""

    @classmethod
    def _rotated_queries(cls, queries: tuple[str, ...] | list[str], offset: int) -> list[str]:
        """Return a rotating but topic-spread query window every hour.

        Categories such as games contain several franchises.  Spreading picks
        across the whole list avoids spending one update on five variants of
        the same title (for example, only Palworld).
        """
        if not queries:
            return []
        size = min(cls._queries_per_category, len(queries))
        start = offset % len(queries)
        # Query lists are intentionally interleaved by topic in interests.json,
        # so a rotating consecutive window contains several different subjects.
        return [queries[(start + index) % len(queries)] for index in range(size)]

    @staticmethod
    def _resolve_queries(queries: tuple[str, ...] | list[str], local_now: datetime) -> list[str]:
        """Keep seasonal anime searches current without yearly config edits."""
        month = local_now.month
        season = "冬季" if month in (12, 1, 2) else "春季" if month in (3, 4, 5) else "夏季" if month in (6, 7, 8) else "秋季"
        return [query.replace("__YEAR__", str(local_now.year)).replace("__SEASON__", season) for query in queries]
