"""Domain models independent of web and output details."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class IntelligenceItem:
    title: str
    url: str
    source: str
    published_at: datetime
    summary: str = ""
    engagement: int = 0
    category: str = "科技"
    tags: tuple[str, ...] = ()


@dataclass(frozen=True)
class IntelligenceCluster:
    title: str
    items: tuple[IntelligenceItem, ...]
    category: str
    score: float
    summary: str

    @property
    def signal_label(self) -> str:
        """Make the evidence strength visible instead of implying a fact check."""
        social_sources = {"Dcard", "Reddit", "YouTube", "TikTok"}
        source_set = set(self.sources)
        if len(source_set) >= 2:
            return "多個平台都在討論"
        if "Google 熱門搜尋" in source_set:
            return "很多人正在搜尋"
        if source_set & social_sources:
            return "社群正在討論"
        return "值得留意"

    @property
    def why_it_appeared(self) -> str:
        """Explain the signal in everyday language, not data-science terms."""
        source_set = set(self.sources)
        if len(source_set) >= 2:
            return "因為不只一個平台都出現這個話題，所以值得你注意。但仍要看原始資料，確認內容是否正確。"
        if "Google 熱門搜尋" in source_set:
            return "因為這個詞最近被很多台灣人搜尋。這只代表大家好奇，不代表網路上的說法是真的。"
        if "Dcard" in source_set:
            return "因為這個話題近期在 Dcard 有較多愛心或留言，代表不少人正在討論。"
        if "TikTok" in source_set:
            return "因為這個標籤近期在 TikTok 有熱度，代表短影音使用者可能正在關注它。"
        return "因為它近期在這個來源中受到較多關注。"

    @property
    def attention_label(self) -> str:
        """Tell a curious but busy reader why an item may matter personally."""
        text = f"{self.title} {self.summary}".lower()
        if any(word in text for word in ("失火", "火災", "地震", "停電", "事故", "颱風", "淹水", "封路")):
            return "在地突發：可能影響安全、交通或行程"
        if any(word in text for word in ("美股", "台股", "股市", "匯率", "利率", "油價", "反彈", "休市")):
            return "市場有變化：可能影響投資或明天的討論"
        if any(word in text for word in ("優惠", "免費", "兌換", "可以換", "特價", "折扣", "贈品", "好康")):
            return "限時好康：可能省錢或值得順路看看"
        if any(word in text for word in ("codex", "gpt", "openai", "ai", "人工智慧")):
            return "科技大事：可能改變你之後怎麼用 AI"
        return "大家正在聊：先看白話重點，再決定要不要深入"

    @property
    def sources(self) -> tuple[str, ...]:
        return tuple(sorted({item.source for item in self.items}))

    @property
    def primary_url(self) -> str:
        return self.items[0].url


@dataclass(frozen=True)
class DailyReport:
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    clusters: tuple[IntelligenceCluster, ...] = ()
    source_errors: tuple[str, ...] = ()
    mode: str = "demo"
