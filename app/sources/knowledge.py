"""Small editorial knowledge collection with primary-source attribution.

This is an offline, reviewed collection, NOT newly fetched news. Selection changes
by Taiwan calendar day, not every report run. The finite pool intentionally repeats.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from app.domain.models import IntelligenceItem


REVIEWED_AT = datetime(2026, 10, 7, tzinfo=timezone(timedelta(hours=8)))
FACTS: tuple[tuple[str, str, str], ...] = (
    ("章魚不是只有一顆心臟，而是三顆", "章魚有三顆心臟：兩顆協助把血送往鰓，一顆把血送往身體其餘部位。下次看到章魚，可以想成牠有分工的循環系統。", "https://ocean.si.edu/ocean-life/invertebrates/octopuses-squids-and-relatives"),
    ("金星轉一圈，比繞太陽一圈還久", "金星自轉一圈約需 243 個地球日，公轉一圈約 225 日。這裡比的是自轉週期，不是日出到下一次日出的時間；後者約 117 日。", "https://science.nasa.gov/venus/venus-facts/"),
    ("火星的夕陽附近，可能呈現藍色", "地球常見紅橙色夕陽，火星卻能出現藍色夕陽。NASA 說明，火星大氣中的細微塵埃讓太陽附近的散射光呈現不同顏色；不是整片天空都一定變藍。", "https://www.nasa.gov/solar-system/nasa-scientist-simulates-sunsets-on-other-worlds/"),
    ("月球每年離地球遠一點，約 3.8 公分", "月球目前平均每年遠離地球約 3.8 公分。這是長期的變化速率，不代表月球和地球每天的距離都只增加；橢圓軌道也會讓距離週期變動。", "https://www.nasa.gov/centers-and-facilities/jpl/saturns-moon-titan-drifting-away-faster-than-previously-thought/"),
    ("鯊魚的骨架，和你的耳朵有共同點", "鯊魚的骨架主要由軟骨組成，不是一般硬骨魚的骨頭。你的耳朵與鼻尖也有軟骨，但鯊魚的結構不等於軟趴趴、沒有支撐。", "https://www.fisheries.noaa.gov/national/outreach-and-education/fun-facts-about-shocking-sharks"),
    ("水可以在特定條件下，固液氣三態共存", "水在特定溫度與壓力的三相點，可讓冰、液態水和水蒸氣共存。標準同位素組成的水約在 0.01°C、特定低壓下達到這個條件，不是日常室內都會發生。", "https://www.nist.gov/si-redefinition/kelvin/kelvin-present-realization"),
)


class KnowledgeSource:
    name = "冷知識精選"

    def __init__(self, day: date | None = None) -> None:
        self.day = day

    def fetch(self) -> list[IntelligenceItem]:
        """Three distinct, daily-stable facts; no network and no invented recency."""
        day = self.day or datetime.now(timezone(timedelta(hours=8))).date()
        start = day.toordinal() % len(FACTS)
        selected = [FACTS[(start + index) % len(FACTS)] for index in range(3)]
        return [IntelligenceItem(title, url, self.name, REVIEWED_AT, summary, category="冷知識")
                for title, summary, url in selected]
