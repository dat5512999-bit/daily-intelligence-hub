"""GitHub Trending public-page source."""

from __future__ import annotations

import re
from html import unescape

from app.domain.models import IntelligenceItem
from app.infrastructure.http_client import get_text
from app.sources.base import utc_now


class GitHubTrendingSource:
    name = "GitHub Trending"

    def fetch(self) -> list[IntelligenceItem]:
        html = get_text("https://github.com/trending?since=daily")
        result: list[IntelligenceItem] = []
        seen: set[str] = set()
        # Page navigation also uses two-part URLs. Only a repository heading
        # inside a Trending article is evidence that the repo is on the list.
        for article in re.findall(r"<article\b[^>]*>(.*?)</article>", html, re.DOTALL | re.IGNORECASE):
            heading = re.search(r"<h2\b[^>]*>(.*?)</h2>", article, re.DOTALL | re.IGNORECASE)
            match = re.search(r'href="/([\w.-]+/[\w.-]+)"', heading.group(1)) if heading else None
            if not match or match.group(1) in seen:
                continue
            repo = match.group(1)
            seen.add(repo)
            paragraph = re.search(r"<p\b[^>]*>(.*?)</p>", article, re.DOTALL | re.IGNORECASE)
            description = " ".join(re.sub(r"<[^>]+>", " ", unescape(paragraph.group(1))).split()) if paragraph else ""
            original_description = description[:1000]
            # An untranslated description cannot serve as a Chinese briefing.
            if not re.search(r"[\u4e00-\u9fff]", description):
                description = ""
            result.append(IntelligenceItem(f"GitHub 今日熱門專案：{repo}", f"https://github.com/{repo}", self.name, utc_now(), description, 0, "GitHub", repo_description=original_description))
            if len(result) >= 12:
                break
        if not result:
            raise RuntimeError("No repositories were found; GitHub page format may have changed.")
        return result
