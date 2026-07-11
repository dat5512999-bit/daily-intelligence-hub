"""Dependency inversion interfaces for plugins and renderers."""

from __future__ import annotations

from typing import Protocol

from app.domain.models import DailyReport, IntelligenceItem


class Source(Protocol):
    name: str

    def fetch(self) -> list[IntelligenceItem]: ...


class Renderer(Protocol):
    def render(self, report: DailyReport) -> str: ...
