"""Quality filters for raw source items."""

from app.domain.models import IntelligenceItem


def filter_items(items: list[IntelligenceItem]) -> list[IntelligenceItem]:
    """Remove malformed and repeated source records while preserving source diversity."""
    seen: set[tuple[str, str]] = set()
    result: list[IntelligenceItem] = []
    for item in items:
        key = (item.source, item.url)
        if not item.title.strip() or not item.url.startswith("http") or key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result
