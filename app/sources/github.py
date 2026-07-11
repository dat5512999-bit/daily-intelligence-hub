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
                result.append(IntelligenceItem(repo, f"https://github.com/{repo}", self.name, utc_now(), "Trending open-source repository on GitHub today.", 0, "GitHub"))
        if not result:
            raise RuntimeError("No repositories were found; GitHub page format may have changed.")
        return result
