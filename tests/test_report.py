from __future__ import annotations

import unittest
from datetime import datetime, timezone

from app.analyzer.filter import filter_items
from app.analyzer.ranking import rank_items
from app.application.generate_daily_report import GenerateDailyReport
from app.domain.models import IntelligenceItem
from app.infrastructure.demo_data import DemoSource
from app.output.html_preview import HtmlPreviewRenderer
from app.output.markdown import MarkdownRenderer
from app.output.assets import APP_ICON_SVG, WEB_MANIFEST
from app.infrastructure.interests import load_interest_profile
from app.sources.dcard import DcardSource
from app.sources.youtube import YouTubeSource


class FailingSource:
    name = "Broken"

    def fetch(self) -> list[IntelligenceItem]:
        raise RuntimeError("expected test failure")


class DiscoveryOnlySource:
    name = "Dcard"

    def fetch(self) -> list[IntelligenceItem]:
        now = datetime.now(timezone.utc)
        return [
            IntelligenceItem("小眾生活話題突然變多人討論", "https://example.com/social", "Dcard", now, "不一定是新聞，但可能是社群苗頭。", 30, "社群冷門雷達")
        ]


class ReportTests(unittest.TestCase):
    def test_filter_removes_invalid_and_duplicates(self) -> None:
        now = datetime.now(timezone.utc)
        valid = IntelligenceItem("Valid", "https://example.com", "Test", now)
        self.assertEqual(filter_items([valid, valid, IntelligenceItem("", "https://bad", "Test", now)]), [valid])

    def test_filter_removes_low_context_trends(self) -> None:
        now = datetime.now(timezone.utc)
        valid = IntelligenceItem("鬼滅之刃 新電影消息", "https://example.com/anime", "Google News", now)
        meet = IntelligenceItem("meet", "https://example.com/meet", "Google 熱門搜尋", now)
        tag = IntelligenceItem("TikTok 熱門標籤：#fff", "https://example.com/tiktok", "TikTok", now)
        code_like_tag = IntelligenceItem("TikTok 熱門標籤：#184d0a__a", "https://example.com/tiktok-code", "TikTok", now)
        self.assertEqual(filter_items([valid, meet, tag, code_like_tag]), [valid])

    def test_ranking_rewards_cross_source_confirmation(self) -> None:
        now = datetime.now(timezone.utc)
        first = IntelligenceItem("Open source AI launch today", "https://one.example", "GitHub", now, engagement=10)
        second = IntelligenceItem("AI launch today open source", "https://two.example", "Hacker News", now, engagement=10)
        single = IntelligenceItem("A separate low signal story", "https://three.example", "Reddit", now, engagement=10)
        clusters = rank_items([first, second, single])
        self.assertEqual(len(clusters[0].items), 2)
        self.assertGreater(clusters[0].score, clusters[1].score)
        self.assertEqual(clusters[0].signal_label, "多個平台都在討論")

    def test_ranking_keeps_interest_mix_for_lazy_reader(self) -> None:
        now = datetime.now(timezone.utc)
        stock_items = [
            IntelligenceItem(f"台股 焦點 {index}", f"https://stock.example/{index}", "Google News", now, engagement=100, category="股票與市場")
            for index in range(6)
        ]
        ai = IntelligenceItem("Codex 新功能", "https://ai.example", "Google News", now, engagement=5, category="AI／Codex")
        game = IntelligenceItem("GTA 6 最新消息", "https://game.example", "Google News", now, engagement=5, category="遊戲與電競")
        anime = IntelligenceItem("無職轉生 新消息", "https://anime.example", "Google News", now, engagement=5, category="動漫與娛樂")

        categories = [cluster.category for cluster in rank_items([*stock_items, ai, game, anime], limit=5)]

        self.assertIn("AI／Codex", categories)
        self.assertIn("遊戲與電競", categories)
        self.assertIn("動漫與娛樂", categories)
        self.assertLessEqual(categories.count("股票與市場"), 3)

    def test_single_social_source_is_never_presented_as_verified(self) -> None:
        now = datetime.now(timezone.utc)
        cluster = rank_items([IntelligenceItem("近期生活話題", "https://example.com/post", "Dcard", now)])[0]
        self.assertEqual(cluster.signal_label, "社群正在討論")

    def test_attention_labels_explain_personal_relevance(self) -> None:
        now = datetime.now(timezone.utc)
        fire = rank_items([IntelligenceItem("一中街失火", "https://example.com/fire", "Google News", now)])[0]
        deal = rank_items([IntelligenceItem("藥局有陀螺可以兌換", "https://example.com/deal", "Dcard", now)])[0]
        stock = rank_items([IntelligenceItem("聯電與機器人概念股成為焦點", "https://example.com/stock", "Google News", now)])[0]
        self.assertIn("在地突發", fire.attention_label)
        self.assertIn("限時好康", deal.attention_label)
        self.assertIn("持股雷達", stock.attention_label)

    def test_report_continues_when_one_source_fails(self) -> None:
        report = GenerateDailyReport([DemoSource(), FailingSource()]).run("demo")
        self.assertTrue(report.clusters)
        self.assertEqual(len(report.source_errors), 1)

    def test_discovery_source_can_bypass_interest_terms(self) -> None:
        report = GenerateDailyReport([DiscoveryOnlySource()], load_interest_profile()).run("demo")
        self.assertEqual(report.clusters[0].category, "社群冷門雷達")

    def test_renderers_produce_expected_content(self) -> None:
        report = GenerateDailyReport([DemoSource()]).run("demo")
        markdown = MarkdownRenderer().render(report)
        preview = HtmlPreviewRenderer().render(report)
        self.assertIn("現在紅什麼／冷門苗頭", markdown)
        self.assertIn("持股雷達", markdown)
        self.assertIn("台灣時間", markdown)
        self.assertNotIn("UTC", markdown)
        self.assertIn("<!doctype html>", preview)
        self.assertIn("manifest.webmanifest", preview)
        self.assertIn("app-icon.svg", preview)
        self.assertIn("今天紅什麼", preview)
        self.assertIn("category-tabs", preview)
        self.assertIn("生活流行", preview)
        self.assertIn("台灣時間", preview)
        self.assertNotIn("UTC", preview)
        self.assertIn("則持股", preview)
        self.assertIn("多看這類", preview)
        self.assertIn("少看這類", preview)
        self.assertIn("情報安全提示", preview)
        self.assertIn("繁中翻譯", preview)
        self.assertIn("白話重點", markdown)
        self.assertIn("今天紅什麼", WEB_MANIFEST)
        self.assertIn("<svg", APP_ICON_SVG)

    def test_html_channel_can_show_multiple_items_per_category(self) -> None:
        now = datetime.now(timezone.utc)
        items = [
            IntelligenceItem("幻獸帕魯 1.0 更新", "https://example.com/palworld-1", "Google News", now, category="遊戲與電競"),
            IntelligenceItem("Palworld Game Pass 消息", "https://example.com/palworld-2", "Google News", now, category="遊戲與電競"),
            IntelligenceItem("幻獸帕魯 卡牌消息", "https://example.com/palworld-3", "Google News", now, category="遊戲與電競"),
            IntelligenceItem("Re:0 周邊活動", "https://example.com/anime-1", "Google News", now, category="動漫與娛樂"),
            IntelligenceItem("鬼滅之刃 電影消息", "https://example.com/anime-2", "Google News", now, category="動漫與娛樂"),
        ]
        clusters = tuple(rank_items(items, limit=5))
        preview = HtmlPreviewRenderer().render(type("Report", (), {"generated_at": now, "clusters": clusters, "source_errors": (), "mode": "demo"})())

        self.assertIn("幻獸帕魯 1.0 更新", preview)
        self.assertIn("Palworld Game Pass 消息", preview)
        self.assertIn("幻獸帕魯 卡牌消息", preview)
        self.assertIn("Re:0 周邊活動", preview)
        self.assertIn("鬼滅之刃 電影消息", preview)

    def test_dcard_lifestyle_mapping_and_taichung_exception(self) -> None:
        self.assertEqual(DcardSource._category("閒聊", "最近小紅書流行餐廳", ""), "生活流行")
        self.assertEqual(DcardSource._category("美食", "台中一中街新餐廳", "限時活動"), "台中好康與活動")

    def test_profile_catches_new_game_interests(self) -> None:
        profile = load_interest_profile()
        now = datetime.now(timezone.utc)
        forza = IntelligenceItem("Forza Horizon 6 地平線6 傳聞", "https://example.com/forza", "Google News", now, category="遊戲與電競")
        warcraft = IntelligenceItem("魔獸爭霸 寒冰霸權 玩家回流", "https://example.com/warcraft", "Google News", now, category="遊戲與電競")
        self.assertTrue(profile.matches(forza))
        self.assertTrue(profile.matches(warcraft))

    def test_youtube_source_is_safe_without_configured_channels(self) -> None:
        """An empty starter configuration must not block a Live report."""
        self.assertEqual(YouTubeSource().fetch(), [])

    def test_profile_rejects_unrelated_virality(self) -> None:
        profile = load_interest_profile()
        now = datetime.now(timezone.utc)
        relevant = IntelligenceItem("Codex 新功能", "https://example.com/codex", "Google News", now, category="AI／Codex")
        unrelated = IntelligenceItem("一般居家料理", "https://example.com/food", "Google News", now, category="美食生活")
        self.assertTrue(profile.matches(relevant))
        self.assertFalse(profile.matches(unrelated))


if __name__ == "__main__":
    unittest.main()
