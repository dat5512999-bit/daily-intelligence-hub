"""Free public TikTok trend entry point.

Creative Center can change its page structure, so this source intentionally
returns only stable trend cards when they are detectable and otherwise does not
block the report. The report never treats a TikTok trend as verified news.
"""

from __future__ import annotations

import re

from app.domain.models import IntelligenceItem
from app.infrastructure.http_client import get_text
from app.sources.base import utc_now


class TikTokTrendsSource:
    name = "TikTok"
    _url = "https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag/pc/en?countryCode=TW&period=7"
    _blocked_tags = {"fff", "fyp", "fy", "viral", "trend", "xyzbca"}

    def fetch(self) -> list[IntelligenceItem]:
        html = get_text(self._url)
        detected = list(dict.fromkeys(re.findall(r"#([\w\u4e00-\u9fff]{2,50})", html)))
        hashtags = [
            hashtag for hashtag in detected
            if hashtag.lower() not in self._blocked_tags and not re.fullmatch(r"[a-z]{2,4}", hashtag.lower())
        ][:10]
        return [IntelligenceItem(f"TikTok 熱門標籤：#{hashtag}", self._url, self.name, utc_now(), "TikTok Creative Center 的台灣公開趨勢訊號，僅代表內容熱度。", 0, "短影音趨勢") for hashtag in hashtags]
