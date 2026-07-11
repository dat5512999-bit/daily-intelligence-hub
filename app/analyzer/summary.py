"""Deterministic, API-key-free summaries for the MVP."""

from app.domain.models import IntelligenceItem


def summarize(items: tuple[IntelligenceItem, ...]) -> str:
    """Produce a compact, evidence-bound summary without inventing facts."""
    lead = items[0]
    text = lead.summary.strip() or lead.title
    text = " ".join(text.split())
    if len(text) > 150:
        text = text[:147].rstrip() + "…"
    if len(items) > 1:
        return f"{text}（另有 {len(items) - 1} 個來源提及）"
    return text
