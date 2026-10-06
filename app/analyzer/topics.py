"""Specific subject labels for browser-local presentation preferences."""

from __future__ import annotations

TOPICS: dict[str, tuple[str, ...]] = {
    "Codex": ("codex",), "ChatGPT": ("chatgpt", "gpt"),
    "幻獸帕魯": ("幻獸帕魯", "palworld", "帕魯"),
    "GTA": ("gta", "grand theft auto"), "地平線": ("forza", "地平線"),
    "魔獸爭霸": ("魔獸爭霸", "warcraft", "寒冰霸權"), "SF Online": ("sf online", "special force"),
    "Re:0": ("re:0", "re:zero", "從零開始"), "無職轉生": ("無職轉生",),
    "轉生史萊姆": ("史萊姆",), "影之強者": ("影之強者",), "海賊王": ("海賊王", "航海王"),
    "犬夜叉": ("犬夜叉",), "火影忍者": ("火影",), "我獨自升級": ("我獨自升級",),
    "實力至上主義": ("實力至上",), "盾之勇者": ("盾之勇者",),
    "進擊的巨人": ("進擊",), "鬼滅之刃": ("鬼滅",), "吉卜力／宮崎駿": ("吉卜力", "宮崎駿"),
    "聯電": ("聯電",), "臻鼎": ("臻鼎",), "0050": ("0050", "元大台灣50"),
    "精材": ("精材",), "群創": ("群創",), "星宇航空": ("星宇",), "機器人": ("機器人",),
    "NBA": ("nba",), "足球": ("足球",), "咖啡": ("咖啡",), "餐廳": ("餐廳",),
    "演唱會": ("演唱會",), "展覽": ("展覽",), "桃子水": ("桃子水",),
}


def topic_for(title: str) -> str:
    """Return a named topic, never silently treat a whole category as one topic."""
    lowered = title.lower()
    return next((label for label, aliases in TOPICS.items() if any(alias in lowered for alias in aliases)), "")
