"""Domain models independent of web and output details."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from urllib.parse import parse_qs, urlparse


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
        watched_stocks = ("聯電", "臻鼎", "0050", "元大台灣50", "精材", "群創", "星宇", "星宇航空", "機器人")
        if any(word.lower() in text for word in watched_stocks):
            return "持股雷達：和你目前關注的股票或概念股有關"
        if any(word in text for word in ("失火", "火災", "地震", "停電", "事故", "颱風", "淹水", "封路")):
            return "在地突發：可能影響安全、交通或行程"
        anime_terms = ("re:zero", "從零開始", "無職轉生", "轉生史萊姆", "影之強者", "海賊王", "犬夜叉", "火影忍者", "我獨自升級", "實力至上主義", "盾之勇者", "進擊的巨人", "鬼滅之刃", "宮崎駿", "吉卜力", "周邊", "聖地巡禮")
        if any(word in text for word in anime_terms):
            return "動漫雷達：可能有新消息、周邊、聯動或聖地巡禮"
        game_terms = ("幻獸帕魯", "palworld", "gta", "sf online", "special force", "地平線", "forza", "魔獸爭霸", "warcraft", "寒冰霸權", "寒冰爭霸", "steam", "電競", "巔峰對決")
        if any(word in text for word in game_terms):
            return "遊戲雷達：可能是新作、更新、玩家回流或社群討論"
        lifestyle_terms = ("dcard", "小紅書", "餐廳", "美食", "穿搭", "景點", "打卡", "網美", "甜點", "咖啡", "開箱", "種草", "感情", "有趣", "閒聊", "迷因")
        if any(word in text for word in lifestyle_terms):
            return "生活苗頭：可能是年輕人正在聊、正在收藏或正在跟風"
        if any(word in text for word in ("美股", "台股", "股市", "匯率", "利率", "油價", "反彈", "休市")):
            return "市場有變化：可能影響投資或明天的討論"
        if any(word in text for word in ("優惠", "免費", "兌換", "可以換", "特價", "折扣", "贈品", "好康")):
            return "限時好康：可能省錢或值得順路看看"
        if any(word in text for word in ("codex", "gpt", "openai", "ai", "人工智慧")):
            return "科技大事：可能改變你之後怎麼用 AI"
        return "大家正在聊：先看白話重點，再決定要不要深入"

    @property
    def decision_label(self) -> str:
        """Give a busy reader an explicit time-spending recommendation."""
        text = f"{self.title} {self.summary}".lower()
        urgent_terms = ("失火", "火災", "地震", "停電", "事故", "颱風", "淹水", "封路")
        watched_stocks = ("聯電", "臻鼎", "0050", "元大台灣50", "精材", "群創", "星宇", "星宇航空", "機器人")
        event_terms = ("展覽", "市集", "演唱", "活動", "嘉年華", "旅遊", "餐廳", "優惠", "兌換")
        if any(term in text for term in urgent_terms):
            return "現在看｜可能影響今天行程"
        if any(term.lower() in text for term in watched_stocks):
            return "現在看｜和你的持股有關"
        if any(term in text for term in event_terms):
            return "有空看｜可能用得到的生活安排"
        if self.category in {"AI／Codex", "遊戲與電競", "動漫與娛樂"}:
            return "值得看｜花 1 分鐘掌握重點"
        return "路過知道即可｜不必急著點開"

    @property
    def source_type_label(self) -> str:
        """Show what kind of evidence a card is based on, not just its source name."""
        source_set = set(self.sources)
        if len(source_set) >= 2:
            return "跨來源整理"
        if "觀光署活動" in source_set:
            return "官方公開資訊"
        if "Google 熱門搜尋" in source_set:
            return "搜尋熱度"
        if source_set & {"Dcard", "Reddit", "TikTok", "YouTube"}:
            return "社群討論"
        if source_set & {"GitHub", "GitHub Trending", "Hacker News"}:
            return "開發者社群"
        return "媒體報導"

    @property
    def sources(self) -> tuple[str, ...]:
        return tuple(sorted({item.source for item in self.items}))

    @property
    def primary_url(self) -> str:
        return self.items[0].url

    @property
    def image_url(self) -> str:
        """Use only source-owned images that can be derived without scraping artwork."""
        item = self.items[0]
        if item.source == "YouTube":
            video_id = parse_qs(urlparse(item.url).query).get("v", [""])[0]
            return f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg" if video_id else ""
        return ""


@dataclass(frozen=True)
class DailyReport:
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    clusters: tuple[IntelligenceCluster, ...] = ()
    source_errors: tuple[str, ...] = ()
    mode: str = "demo"

    @property
    def source_count(self) -> int:
        """Count the distinct sources that actually made it into the report."""
        return len({source for cluster in self.clusters for source in cluster.sources})

    @property
    def health_label(self) -> str:
        """Never present a thin or partially failed report as fully healthy."""
        if not self.clusters:
            return "資料不足"
        if self.source_count < 3:
            return "資訊來源不足"
        if self.source_errors:
            return "部分來源受限"
        return "來源正常"

    @property
    def health_note(self) -> str:
        """Give the mobile reader a plain-language next action."""
        if not self.clusters:
            return "本次沒有足夠的即時資料；請稍後再更新，不會以範例內容冒充。"
        if self.source_count < 3:
            return "本次只取得少量來源，先當速報參考；下一輪會自動再抓。"
        if self.source_errors:
            return "部分社群來源暫時受限；其餘公開來源仍已完成整理。"
        return "多個公開來源已完成整理；社群話題仍請開啟原文確認。"
