"""User-owned, file-based interest configuration with no account or database."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from app.domain.models import IntelligenceItem


@dataclass(frozen=True)
class InterestCategory:
    name: str
    queries: tuple[str, ...]
    terms: tuple[str, ...]
    priority: int


class InterestProfile:
    def __init__(self, categories: tuple[InterestCategory, ...]) -> None:
        self.categories = categories

    @property
    def category_names(self) -> tuple[str, ...]:
        return tuple(category.name for category in self.categories)

    def matches(self, item: IntelligenceItem) -> bool:
        """Keep items relevant to the person's chosen topics, not generic virality."""
        if item.category in self.category_names:
            return True
        searchable = f"{item.title} {item.summary}".lower()
        return any(term.lower() in searchable for category in self.categories for term in category.terms)

    def category_for(self, text: str) -> str | None:
        lowered = text.lower()
        matched = [category for category in self.categories if any(term.lower() in lowered for term in category.terms)]
        return max(matched, key=lambda category: category.priority).name if matched else None

    def priority_for(self, category_name: str) -> int:
        return next((category.priority for category in self.categories if category.name == category_name), 0)


def load_interest_profile(path: Path = Path("config/interests.json")) -> InterestProfile:
    payload = json.loads(path.read_text(encoding="utf-8"))
    categories = tuple(InterestCategory(str(row["name"]), tuple(map(str, row["queries"])), tuple(map(str, row["terms"])), int(row["priority"])) for row in payload["categories"])
    return InterestProfile(categories)
