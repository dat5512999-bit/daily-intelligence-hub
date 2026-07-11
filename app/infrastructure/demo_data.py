"""Offline, deterministic source data used for preview and tests."""

from datetime import datetime, timedelta, timezone

from app.domain.models import IntelligenceItem


class DemoSource:
    name = "Demo"

    def fetch(self) -> list[IntelligenceItem]:
        now = datetime.now(timezone.utc)
        return [
            IntelligenceItem("Codex 與 GPT 工作流程的新整合", "https://example.com/codex", "GitHub", now - timedelta(hours=2), "AI 工具的整合可能讓你未來少切換幾個服務，就能完成更多工作。", 1250, "AI／Codex"),
            IntelligenceItem("GTA 與幻獸帕魯玩家正在討論的新內容", "https://example.com/games", "Reddit", now - timedelta(hours=3), "遊戲社群正在討論更新內容與接下來值得玩的活動。", 820, "遊戲與電競"),
            IntelligenceItem("無職轉生相關動畫消息與社群討論", "https://example.com/anime", "Google News", now - timedelta(hours=4), "動漫迷正在討論作品後續消息與最新內容。", 0, "動漫與娛樂"),
            IntelligenceItem("台中市區火災影響周邊交通", "https://example.com/taichung", "Google News", now - timedelta(hours=1), "在地突發事件可能影響附近安全與交通，出門前值得確認。", 0, "台中現在要注意"),
            IntelligenceItem("台中週末展覽與限時活動整理", "https://example.com/events", "Dcard", now - timedelta(hours=6), "近期有展覽、演唱會與限時活動可安排週末行程。", 950, "台中好康與活動"),
            IntelligenceItem("美股反彈與台股休市的市場焦點", "https://example.com/stocks", "Google News", now - timedelta(hours=5), "美股變化可能影響下一個台股交易日的市場情緒；這不是買賣建議。", 0, "股票與市場"),
        ]
