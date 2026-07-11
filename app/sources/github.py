"""GitHub Trending public-page source."""

from __future__ import annotations

import re

from app.domain.models import IntelligenceItem
from app.infrastructure.http_client import get_text
from app.sources.base import utc_now


class GitHubTrendingSource:
    name = "GitHub Trending"

    def fetch(self) -> list[IntelligenceItem]:
        html = get_text("https://github.com/trending?since=daily")
        repositories = re.findall(r'href="/([\w.-]+/[\w.-]+)"', html)
        result: list[IntelligenceItem] = []
        for repo in dict.fromkeys(repositories):
            if repo.count("/") == 1 and len(result) < 12:
                result.append(IntelligenceItem(f"GitHub 今日熱門專案：{repo}", f"https://github.com/{repo}", self.name, utc_now(), "今天在 GitHub 熱門榜出現的開源專案；是否值得點開，請依名稱和原始介紹判斷。", 0, "GitHub"))
        if not result:
            raise RuntimeError("No repositories were found; GitHub page format may have changed.")
        return result
