"""Offline, deterministic source data used for preview and tests."""

from datetime import datetime, timedelta, timezone

from app.domain.models import IntelligenceItem


class DemoSource:
    name = "Demo"

    def fetch(self) -> list[IntelligenceItem]:
        now = datetime.now(timezone.utc)
        return [
            IntelligenceItem("Codex 與 GPT 工作流程的新整合", "https://example.com/codex", "GitHub", now - timedelta(hours=2), "AI 工具的整合可能讓你未來少切換幾個服務，就能完成更多工作。", 1250, "AI／Codex"),
            IntelligenceItem("GitHub 今日熱門專案：openai/codex", "https://github.com/openai/codex", "GitHub Trending", now - timedelta(hours=2), "今天在 GitHub 熱門榜出現的開源專案；是否值得點開，請依名稱和原始介紹判斷。", 700, "GitHub"),
            IntelligenceItem("GitHub 今日熱門專案：browser-use/browser-use", "https://github.com/browser-use/browser-use", "GitHub Trending", now - timedelta(hours=2), "能讓 AI 操作瀏覽器的開源工具近期受到開發者注意。", 620, "GitHub"),
            IntelligenceItem("GitHub 今日熱門專案：unclecode/crawl4ai", "https://github.com/unclecode/crawl4ai", "GitHub Trending", now - timedelta(hours=3), "公開網頁整理與內容擷取工具，適合快速知道用途後再決定是否深入。", 580, "GitHub"),
            IntelligenceItem("萊爾富桃子水引發搶購與到貨討論", "https://example.com/peach-water", "Google News", now - timedelta(hours=2), "便利商店限量新品如果大量缺貨、開箱或交換到貨情報，通常就是正在出圈的生活流行。", 0, "年輕人流行"),
            IntelligenceItem("年輕人用已讀與貼圖取代長篇溝通", "https://example.com/young-communication", "Google News", now - timedelta(hours=4), "這類話題反映社群溝通習慣改變，適合先了解現象，不把單一文章當成整個世代。", 0, "年輕人流行"),
            IntelligenceItem("近期爆紅的國內外網美打卡景點", "https://example.com/trending-spots", "Google News", now - timedelta(hours=5), "整理近期社群反覆出現的拍照地點，方便判斷是否值得排進旅遊行程。", 0, "年輕人流行"),
            IntelligenceItem("GTA 與幻獸帕魯玩家正在討論的新內容", "https://example.com/games", "Reddit", now - timedelta(hours=3), "遊戲社群正在討論更新內容與接下來值得玩的活動。", 820, "遊戲與電競"),
            IntelligenceItem("幻獸帕魯 1.0 大型更新與價格消息", "https://example.com/palworld-1", "Google News", now - timedelta(hours=3), "這類消息可能包含版本更新、價格、Game Pass 或玩家回流資訊，適合遊戲玩家快速掃過。", 0, "遊戲與電競"),
            IntelligenceItem("幻獸帕魯卡牌與周邊話題升溫", "https://example.com/palworld-2", "Google News", now - timedelta(hours=4), "遊戲熱度常會延伸到卡牌、周邊與收藏市場，值得留意是否出圈。", 0, "遊戲與電競"),
            IntelligenceItem("SF Online 懷舊服與老玩家回流討論", "https://example.com/sf-online", "Dcard", now - timedelta(hours=4), "有些遊戲不是最大新聞，但社群突然懷舊、揪團或回鍋，就很像你想知道的冷門流行苗頭。", 510, "遊戲與電競"),
            IntelligenceItem("地平線6與 GTA 6 玩家期待清單升溫", "https://example.com/forza-gta", "Google News", now - timedelta(hours=6), "大型遊戲的新作傳聞、上市節奏與玩家期待，通常會在社群先熱起來。", 0, "遊戲與電競"),
            IntelligenceItem("Re:0、無職轉生與鬼滅之刃周邊活動整理", "https://example.com/anime", "Google News", now - timedelta(hours=4), "這類情報可能包含新一季消息、電影、周邊、遊戲聯動或聖地巡禮，適合動漫興趣者快速掃過。", 0, "動漫與娛樂"),
            IntelligenceItem("宮崎駿與吉卜力展覽旅遊話題升溫", "https://example.com/ghibli", "Dcard", now - timedelta(hours=5), "動漫不只看作品，也可能延伸到展覽、旅遊景點與拍照打卡行程。", 420, "動漫與娛樂"),
            IntelligenceItem("我獨自升級與影之強者遊戲聯動討論", "https://example.com/anime-game", "Reddit", now - timedelta(hours=5), "動漫 IP 如果延伸到手遊或聯名活動，通常比單純新聞更容易吸引粉絲參與。", 250, "動漫與娛樂"),
            IntelligenceItem("NBA 球員交易與自由市場動向", "https://example.com/nba-trade", "Google News", now - timedelta(hours=2), "快速掌握重要球員去哪一隊，以及可能改變球隊戰力的交易。", 0, "運動焦點"),
            IntelligenceItem("台灣籃球與足球本週比賽焦點", "https://example.com/taiwan-sports", "Google News", now - timedelta(hours=3), "整理台灣近期值得注意的賽程、結果與代表隊消息。", 0, "運動焦點"),
            IntelligenceItem("挪威足球與歐洲聯賽近況", "https://example.com/norway-football", "Google News", now - timedelta(hours=4), "從國家隊、球員與歐洲聯賽角度快速了解挪威足球最近發生什麼事。", 0, "運動焦點"),
            IntelligenceItem("台中市區火災影響周邊交通", "https://example.com/taichung", "Google News", now - timedelta(hours=1), "在地突發事件可能影響附近安全與交通，出門前值得確認。", 0, "台中現在要注意"),
            IntelligenceItem("台中週末展覽與限時活動整理", "https://example.com/events", "Dcard", now - timedelta(hours=6), "近期有展覽、演唱會與限時活動可安排週末行程。", 950, "台中好康與活動"),
            IntelligenceItem("聯電、群創與機器人概念股成為台股討論焦點", "https://example.com/stocks", "Google News", now - timedelta(hours=5), "這類消息和你目前關注的持股、ETF 或概念股有關，適合先知道但不要直接當買賣建議。", 0, "股票與市場"),
            IntelligenceItem("Dcard 熱門：台中最近被推的平價約會餐廳", "https://example.com/dcard-food", "Dcard", now - timedelta(hours=3), "生活類不一定是大新聞，但如果很多人收藏、留言或討論，可能就是週末用得到的情報。", 690, "生活流行"),
            IntelligenceItem("小紅書風格打卡點被台灣網友整理討論", "https://example.com/xhs-style", "Google News", now - timedelta(hours=5), "小紅書目前先當作公開搜尋與媒體訊號，不直接登入抓貼文；適合捕捉餐廳、穿搭、景點這類生活苗頭。", 0, "生活流行"),
            IntelligenceItem("Dcard 閒聊：最近大家一直提到的省錢小物", "https://example.com/dcard-life", "Dcard", now - timedelta(hours=6), "這種話題通常很生活，但如果重複出現，就代表它可能正在年輕族群之間擴散。", 480, "生活流行"),
            IntelligenceItem("大樹藥局分店有人在換陀螺", "https://example.com/local-deal", "Dcard", now - timedelta(hours=7), "這種地方小情報通常不會變成大新聞，但可能是生活圈裡很實用的限時話題。", 260, "社群冷門雷達"),
            IntelligenceItem("某款小眾手遊角色突然被大量搜尋", "https://example.com/search-trend", "Google 熱門搜尋", now - timedelta(hours=8), "搜尋量上升代表有人開始好奇，可能來自活動、實況主或社群迷因。", 0, "搜尋趨勢"),
        ]
