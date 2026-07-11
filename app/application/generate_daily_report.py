"""Application orchestration; failures remain isolated to their source plugin."""

from __future__ import annotations

from app.analyzer.filter import filter_items
from app.analyzer.ranking import rank_items
from app.domain.models import DailyReport, IntelligenceItem
from app.infrastructure.interests import InterestProfile
from app.domain.ports import Source

DISCOVERY_SOURCES = {"Dcard", "Google 熱門搜尋", "TikTok", "Reddit"}


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
                errors.append(f"{source.name}: {error}")
        cleaned = filter_items(collected)
        relevant = [
            item for item in cleaned
            if self._profile is None or self._profile.matches(item) or item.source in DISCOVERY_SOURCES
        ]
        return DailyReport(clusters=tuple(rank_items(relevant, limit=24)), source_errors=tuple(errors), mode=mode)
