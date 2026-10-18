"""A small, original daily reflection collection (not therapy or quotations)."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from app.domain.models import IntelligenceItem


TAIWAN_TIMEZONE = timezone(timedelta(hours=8))

# Each entry pairs one plain-language idea with one small action. These are
# original editorial prompts, not attributed quotes or promises of outcomes.
IDEAS: tuple[tuple[str, str, str], ...] = (
    ("想改善關係，先把在意的事說清楚", "想法：別人不一定猜得到你的感受。今天試試：用「我有點在意……我希望……」說一件小事，不先指責對方。" , "溝通"),
    ("先問清楚，再替對方下結論", "想法：沉默或晚回訊息，不一定代表不在乎。今天試試：把猜測換成一個不帶質問的問題。", "溝通"),
    ("說出需求，不等於要求別人照做", "想法：表達是讓對方了解你；接不接受，仍可以一起討論。今天試試：先說「我想跟你商量一件事」。", "溝通"),
    ("不舒服時，先描述事情，不急著貼標籤", "想法：談具體行為，比說「你就是……」更容易開始對話。今天試試：說明發生了什麼，以及你當下的感受。", "溝通"),
    ("你可以先聽懂，再決定是否同意", "想法：理解對方不等於認輸。今天試試：先用一句話確認「你的意思是……，對嗎？」", "溝通"),
    ("道歉可以從承認影響開始", "想法：解釋原因不一定能消除對方的感受。今天試試：先說「我知道這件事讓你……」，再談怎麼補救。", "溝通"),
    ("把大目標縮小，今天比較容易開始", "想法：不用一次解決全部。今天試試：把想做的事切成一個 10 分鐘內能完成的步驟。", "行動"),
    ("卡住時，換一個更小的問題", "想法：問題太大會讓人不知道從哪裡動手。今天試試：問自己「下一步最小、最具體的動作是什麼？」", "行動"),
    ("休息不是放棄，是先把狀態照顧好", "想法：累的時候硬撐，未必能做得更好。今天試試：離開螢幕幾分鐘、喝水，再決定下一步。", "照顧自己"),
    ("今天做不到全部，不代表今天什麼都沒做", "想法：進度可以很小。今天試試：寫下一件已完成的事，再挑一件最重要的小事。", "照顧自己"),
    ("情緒很滿時，可以晚一點再回覆", "想法：先讓自己有空間，不必立刻把話說完。今天試試：告訴對方「我想整理一下，晚點再回你」。", "照顧自己"),
    ("拒絕一件事，不代表否定一個人", "想法：清楚說明自己的界線，比勉強答應後心裡不舒服更直接。今天試試：簡短說明「這次我沒辦法，但謝謝你想到我」。", "界線"),
    ("想被理解，也可以先告訴別人怎麼幫你", "想法：有時我們需要的是陪伴，不是解法。今天試試：直接說「你先聽我說就好」或「我想一起想辦法」。", "溝通"),
    ("問意見時，先想好自己最想改善哪一點", "想法：具體問題比較容易得到能用的回饋。今天試試：把「你覺得我怎麼樣？」換成「這段說明哪裡最不清楚？」", "學習"),
    ("犯錯後，先分清楚事情和自我評價", "想法：一次失誤是發生過的事，不是整個人的定義。今天試試：寫下「哪一步出錯」和「下次要改哪一步」。", "學習"),
    ("別人的進度，不必直接變成你的期限", "想法：每個人的條件和時程不同。今天試試：把比較改成一個問題：「我欣賞對方哪個做法，可以學一小部分？」", "心態"),
    ("感謝不必很大，小事也算數", "想法：注意到一件小小順利的事，不等於否認今天的困難。今天試試：記下一件讓今天稍微好一點的事。", "心態"),
    ("關係需要修補時，可以先從下一次怎麼做開始", "想法：說明期待比只反覆追究對錯更容易找到方向。今天試試：問「下次遇到這種情況，我們可以怎麼提醒彼此？」", "關係"),
    ("把手機放遠一點，先完成眼前一小段", "想法：環境可以幫你減少分心，不必只靠意志力。今天試試：把手機放到手拿不到的地方 10 分鐘。", "專注"),
    ("想法不必一次說得完美，先求真誠清楚", "想法：練習表達是為了讓對方更懂你，不是比賽。今天試試：先說一個重點，再停下來聽對方怎麼理解。", "溝通"),
    ("今天先做一點，也算是在照顧未來的自己", "想法：小步驟能讓明天少一點負擔。今天試試：替明天準備一樣東西，或先處理一個 5 分鐘的小任務。", "行動"),
)


class DailyBoostSource:
    name = "每日充電精選"

    def __init__(self, day: date | None = None) -> None:
        self.day = day

    def fetch(self) -> list[IntelligenceItem]:
        """Return three distinct, day-stable reflection prompts without a network."""
        day = self.day or datetime.now(TAIWAN_TIMEZONE).date()
        start = (day.toordinal() * 3) % len(IDEAS)
        selected = [IDEAS[(start + offset) % len(IDEAS)] for offset in range(3)]
        return [
            IntelligenceItem(
                title=title,
                # A stable internal identity, not a real navigable website URL.
                url=f"daily-idea://{(start + offset) % len(IDEAS)}",
                source=self.name,
                published_at=datetime.combine(day, datetime.min.time(), TAIWAN_TIMEZONE),
                summary=reflection,
                category="每日充電",
                tags=(topic,),
            )
            for offset, (title, reflection, topic) in enumerate(selected)
        ]
