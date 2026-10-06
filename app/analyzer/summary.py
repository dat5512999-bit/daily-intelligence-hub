"""Deterministic, API-key-free summaries for the MVP."""

from app.domain.models import IntelligenceItem


GENERIC_SUMMARIES = (
    "這則消息符合你關注", "開啟原文可確認", "公開趨勢訊號", "僅代表內容熱度",
    "最近被更多台灣人搜尋", "是否值得點開，請依名稱", "交通部觀光署公開活動資訊；適合查看",
)


def has_useful_summary(item: IntelligenceItem) -> bool:
    """A feed headline or boilerplate is not an article summary."""
    text = item.summary.strip()
    return bool(text and text != item.title.strip() and not any(term in text for term in GENERIC_SUMMARIES))


def summarize(items: tuple[IntelligenceItem, ...]) -> str:
    """Produce a compact, evidence-bound summary without inventing facts."""
    lead = next((item for item in items if has_useful_summary(item)), items[0])
    if not has_useful_summary(lead):
        return "僅取得標題，尚未讀到內文；請看原文確認細節。"
    text = lead.summary.strip()
    text = " ".join(text.split())
    if len(text) > 150:
        text = text[:147].rstrip() + "…"
    if len(items) > 1:
        return f"{text}（另有 {len(items) - 1} 個來源提及）"
    return text
