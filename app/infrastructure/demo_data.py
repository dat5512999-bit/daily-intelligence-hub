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
            IntelligenceItem("幻獸帕魯 1.0 大型更新與價格消息", "https://example.com/palworld-1", "Google News", now - timedelta(hours=3), "這類消息可能包含版本更新、價格、Game Pass 或玩家回流資訊，適合遊戲玩家快速掃過。", 0, "遊戲與電競"),
            IntelligenceItem("幻獸帕魯卡牌與周邊話題升溫", "https://example.com/palworld-2", "Google News", now - timedelta(hours=4), "遊戲熱度常會延伸到卡牌、周邊與收藏市場，值得留意是否出圈。", 0, "遊戲與電競"),
            IntelligenceItem("Re:0、無職轉生與鬼滅之刃周邊活動整理", "https://example.com/anime", "Google News", now - timedelta(hours=4), "這類情報可能包含新一季消息、電影、周邊、遊戲聯動或聖地巡禮，適合動漫興趣者快速掃過。", 0, "動漫與娛樂"),
            IntelligenceItem("宮崎駿與吉卜力展覽旅遊話題升溫", "https://example.com/ghibli", "Dcard", now - timedelta(hours=5), "動漫不只看作品，也可能延伸到展覽、旅遊景點與拍照打卡行程。", 420, "動漫與娛樂"),
            IntelligenceItem("我獨自升級與影之強者遊戲聯動討論", "https://example.com/anime-game", "Reddit", now - timedelta(hours=5), "動漫 IP 如果延伸到手遊或聯名活動，通常比單純新聞更容易吸引粉絲參與。", 250, "動漫與娛樂"),
            IntelligenceItem("台中市區火災影響周邊交通", "https://example.com/taichung", "Google News", now - timedelta(hours=1), "在地突發事件可能影響附近安全與交通，出門前值得確認。", 0, "台中現在要注意"),
            IntelligenceItem("台中週末展覽與限時活動整理", "https://example.com/events", "Dcard", now - timedelta(hours=6), "近期有展覽、演唱會與限時活動可安排週末行程。", 950, "台中好康與活動"),
            IntelligenceItem("聯電、群創與機器人概念股成為台股討論焦點", "https://example.com/stocks", "Google News", now - timedelta(hours=5), "這類消息和你目前關注的持股、ETF 或概念股有關，適合先知道但不要直接當買賣建議。", 0, "股票與市場"),
            IntelligenceItem("大樹藥局分店有人在換陀螺", "https://example.com/local-deal", "Dcard", now - timedelta(hours=7), "這種地方小情報通常不會變成大新聞，但可能是生活圈裡很實用的限時話題。", 260, "社群冷門雷達"),
            IntelligenceItem("某款小眾手遊角色突然被大量搜尋", "https://example.com/search-trend", "Google 熱門搜尋", now - timedelta(hours=8), "搜尋量上升代表有人開始好奇，可能來自活動、實況主或社群迷因。", 0, "搜尋趨勢"),
        ]
