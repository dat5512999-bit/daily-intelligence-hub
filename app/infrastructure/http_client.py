"""Small standard-library HTTP client with a safe timeout."""

from __future__ import annotations

from urllib.request import Request, urlopen


def get_text(url: str, timeout: int = 12) -> str:
    request = Request(url, headers={"User-Agent": "DailyIntelligenceHub/0.1 (+personal research)"})
    with urlopen(request, timeout=timeout) as response:  # nosec B310: URLs are fixed source endpoints.
        return response.read().decode("utf-8", errors="replace")
