"""Application orchestration; failures remain isolated to their source plugin."""

from __future__ import annotations

from app.analyzer.filter import filter_items
from app.analyzer.ranking import rank_items
from app.domain.models import DailyReport, IntelligenceItem
from app.infrastructure.interests import InterestProfile
from app.domain.ports import Source

DISCOVERY_SOURCES = {"Dcard", "Google 熱門搜尋", "TikTok", "Reddit"}


def _friendly_error(source_name: str, error: Exception) -> str:
    """Do not expose Python/network diagnostics to a non-technical reader."""
    detail = str(error)
    if "urlopen error" in detail or "WinError" in detail or "HTTP Error" in detail:
        return f"{source_name}：暫時連線失敗，下一次更新會再試。"
    if len(detail) > 100:
        return f"{source_name}：本輪資料格式異常，已略過並會在下次更新重試。"
    return f"{source_name}：{detail}"


class GenerateDailyReport:
    def __init__(self, sources: list[Source], profile: InterestProfile | None = None) -> None:
        self._sources = sources
        self._profile = profile

    def run(self, mode: str) -> DailyReport:
        collected: list[IntelligenceItem] = []
        errors: list[str] = []
        for source in self._sources:
            try:
                collected.extend(source.fetch())
            except Exception as error:  # Source isolation is an explicit product requirement.
                errors.append(_friendly_error(source.name, error))
        cleaned = filter_items(collected)
        relevant = [
            item for item in cleaned
            if self._profile is None or self._profile.matches(item) or item.source in DISCOVERY_SOURCES
        ]
        # Nine personal channels × three items, plus room for discovery signals.
        # The renderer still stays compact because every channel is collapsed.
        category_capacity = (len(self._profile.categories) * 3 + 9) if self._profile else 36
        return DailyReport(clusters=tuple(rank_items(relevant, limit=max(36, category_capacity))), source_errors=tuple(errors), mode=mode)
