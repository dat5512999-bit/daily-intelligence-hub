from __future__ import annotations

import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from app.analyzer.filter import filter_items
from app.analyzer.ranking import rank_items
from app.application.generate_daily_report import GenerateDailyReport
from app.application.generate_daily_report import _friendly_error
from app.domain.models import IntelligenceItem
from app.infrastructure.demo_data import DemoSource
from app.output.html_preview import HtmlPreviewRenderer
from app.output.markdown import MarkdownRenderer
from app.output.assets import APP_ICON_SVG, WEB_MANIFEST
from app.infrastructure.interests import load_interest_profile
from app.sources.dcard import DcardSource
from app.sources.interest_news import InterestNewsSource
from app.sources.taiwan_events import TaiwanTourismEventsSource
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

    def test_filter_strips_feed_html_and_skips_untranslated_social_posts(self) -> None:
        now = datetime.now(timezone.utc)
        html_summary = IntelligenceItem("台中活動", "https://example.com/event", "Google News", now, "<table><tr><td>週末市集</td></tr></table>")
        english_reddit = IntelligenceItem("I challenged GPT and it completed the challenge", "https://example.com/reddit", "Reddit", now, "<p>English post</p>")
        cleaned = filter_items([html_summary, english_reddit])
        self.assertEqual(len(cleaned), 1)
        self.assertEqual(cleaned[0].summary, "週末市集")

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

    def test_ranking_fills_three_slots_per_category_in_rounds(self) -> None:
        now = datetime.now(timezone.utc)
        titles = {
            "年輕人流行": ("桃子水搶購", "拒絕溝通現象", "海外打卡景點"),
            "遊戲與電競": ("GTA 六代消息", "SF 懷舊玩家", "魔獸改版焦點"),
            "運動焦點": ("NBA 球員異動", "台灣籃球賽程", "挪威足球近況"),
            "GitHub": ("Codex 開源專案", "瀏覽器代理工具", "網頁擷取框架"),
        }
        items = [
            IntelligenceItem(title, f"https://example.com/{category}/{index}", "Google News", now, category=category)
            for category, category_titles in titles.items()
            for index, title in enumerate(category_titles)
        ]
        clusters = rank_items(items, limit=12)
        for category in ("年輕人流行", "遊戲與電競", "運動焦點", "GitHub"):
            self.assertEqual(sum(cluster.category == category for cluster in clusters), 3)

    def test_github_trending_prefix_does_not_merge_different_repositories(self) -> None:
        now = datetime.now(timezone.utc)
        clusters = rank_items([
            IntelligenceItem("GitHub 今日熱門專案：openai/codex", "https://github.com/openai/codex", "GitHub Trending", now, category="GitHub"),
            IntelligenceItem("GitHub 今日熱門專案：browser-use/browser-use", "https://github.com/browser-use/browser-use", "GitHub Trending", now, category="GitHub"),
            IntelligenceItem("GitHub 今日熱門專案：unclecode/crawl4ai", "https://github.com/unclecode/crawl4ai", "GitHub Trending", now, category="GitHub"),
        ])
        self.assertEqual(len(clusters), 3)

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

    def test_decision_and_source_labels_are_plain_and_actionable(self) -> None:
        now = datetime.now(timezone.utc)
        fire = rank_items([IntelligenceItem("台中火災封路", "https://example.com/fire", "Google News", now)])[0]
        event = rank_items([IntelligenceItem("台中週末市集活動", "https://example.com/event", "觀光署活動", now)])[0]
        trend = rank_items([IntelligenceItem("新迷因突然爆紅", "https://example.com/trend", "Google 熱門搜尋", now)])[0]
        self.assertIn("現在看", fire.decision_label)
        self.assertEqual(event.source_type_label, "官方公開資訊")
        self.assertEqual(trend.source_type_label, "搜尋熱度")

    def test_only_youtube_official_thumbnail_is_used_as_an_image(self) -> None:
        now = datetime.now(timezone.utc)
        youtube = rank_items([IntelligenceItem("影片", "https://www.youtube.com/watch?v=abc123", "YouTube", now)])[0]
        github = rank_items([IntelligenceItem("owner/repo", "https://github.com/owner/repo", "GitHub Trending", now)])[0]
        news = rank_items([IntelligenceItem("一般新聞", "https://example.com/news", "Google News", now)])[0]
        self.assertIn("i.ytimg.com/vi/abc123", youtube.image_url)
        self.assertEqual(github.image_url, "")
        self.assertEqual(news.image_url, "")

    def test_report_continues_when_one_source_fails(self) -> None:
        report = GenerateDailyReport([DemoSource(), FailingSource()]).run("demo")
        self.assertTrue(report.clusters)
        self.assertEqual(len(report.source_errors), 1)

    def test_network_errors_are_reader_friendly(self) -> None:
        message = _friendly_error("Google News", OSError("<urlopen error [WinError 10013] access denied>"))
        self.assertEqual(message, "Google News：暫時連線失敗，下一次更新會再試。")

    def test_live_report_with_only_one_source_is_never_called_healthy(self) -> None:
        now = datetime.now(timezone.utc)
        item = IntelligenceItem("只剩一個媒體來源", "https://example.com/news", "Google News", now, category="AI／Codex")
        cluster = rank_items([item])[0]
        report = type("Report", (), {
            "generated_at": now,
            "clusters": (cluster,),
            "source_errors": (),
            "mode": "live",
            "source_count": 1,
            "health_label": "資訊來源不足",
            "health_note": "本次只取得少量來源，先當速報參考；下一輪會自動再抓。",
        })()
        preview = HtmlPreviewRenderer().render(report)
        self.assertIn("資訊來源不足", preview)
        self.assertNotIn("即時連線", preview)

    def test_report_health_identifies_partial_source_failure(self) -> None:
        report = GenerateDailyReport([DemoSource(), FailingSource()]).run("live")
        self.assertEqual(report.health_label, "部分來源受限")
        self.assertGreaterEqual(report.source_count, 3)

    def test_workflow_runs_hourly_away_from_the_top_of_the_hour(self) -> None:
        from pathlib import Path

        workflow = Path(".github/workflows/daily-report.yml").read_text(encoding="utf-8")
        self.assertIn('cron: "17 * * * *"', workflow)

    def test_feedback_is_scoped_to_one_dashboard_item(self) -> None:
        now = datetime.now(timezone.utc)
        cluster = rank_items([IntelligenceItem("同一篇文章", "https://example.com/one", "Google News", now)])[0]
        renderer = HtmlPreviewRenderer()
        compact = renderer._compact_row(cluster, 1, "update")
        self.assertIn('data-item="update:1:https://example.com/one"', compact)

    def test_dashboard_uses_mixed_components_not_category_card_grid(self) -> None:
        report = GenerateDailyReport([DemoSource()]).run("demo")
        preview = HtmlPreviewRenderer().render(report)
        self.assertIn('class="hero"', preview)
        self.assertIn("大家正在關注", preview)
        self.assertIn("你的關注頻道", preview)
        self.assertIn("你的持股雷達", preview)
        self.assertNotIn("category-tabs", preview)

    def test_official_lifestyle_event_source_extracts_events_not_navigation(self) -> None:
        html = """
        <a href="/nav">觀光活動</a>
        <a href="/event/one">2026 台中夏日音樂市集</a>
        <a href="/event/two">台灣國際熱氣球嘉年華</a>
        """
        with patch("app.sources.taiwan_events.get_text", return_value=html):
            items = TaiwanTourismEventsSource().fetch()
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0].source, "觀光署活動")
        self.assertEqual(items[0].category, "台中好康與活動")

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
        self.assertIn("大家正在關注", preview)
        self.assertIn("想看哪類，再點開就好", preview)
        self.assertIn("台灣時間", preview)
        self.assertNotIn("UTC", preview)
        self.assertIn("則持股", preview)
        self.assertIn("有興趣", preview)
        self.assertIn("少一點", preview)
        self.assertIn("data-item=", preview)
        self.assertIn("daily-intelligence-item-feedback-v2", preview)
        self.assertIn("情報判讀", preview)
        self.assertIn("檢查最新頁面", preview)
        self.assertIn("手動產生新報告", preview)
        self.assertIn("https://github.com/dat5512999-bit/daily-intelligence-hub/actions/workflows/daily-report.yml", preview)
        self.assertIn("翻成繁中", preview)
        self.assertIn("白話重點", markdown)
        self.assertIn("建議：", markdown)
        self.assertIn("社群討論", preview)
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
        preview = HtmlPreviewRenderer().render(type("Report", (), {
            "generated_at": now,
            "clusters": clusters,
            "source_errors": (),
            "mode": "demo",
            "source_count": 1,
            "health_label": "來源正常",
            "health_note": "這是測試報告。",
        })())

        self.assertIn("幻獸帕魯 1.0 更新", preview)
        self.assertIn("Palworld Game Pass 消息", preview)
        self.assertIn("幻獸帕魯 卡牌消息", preview)
        self.assertIn("Re:0 周邊活動", preview)
        self.assertIn("鬼滅之刃 電影消息", preview)

    def test_dashboard_shows_visual_cards_only_for_source_owned_images(self) -> None:
        now = datetime.now(timezone.utc)
        clusters = tuple(rank_items([
            IntelligenceItem("YouTube 影片", "https://www.youtube.com/watch?v=abc123", "YouTube", now, category="影音生活"),
            IntelligenceItem("owner/repo", "https://github.com/owner/repo", "GitHub Trending", now, category="GitHub"),
            IntelligenceItem("一般新聞", "https://example.com/news", "Google News", now, category="科技"),
        ]))
        report = type("Report", (), {"generated_at": now, "clusters": clusters, "source_errors": (), "mode": "demo", "source_count": 3, "health_label": "來源正常", "health_note": "測試"})()
        preview = HtmlPreviewRenderer().render(report)
        self.assertIn("影片精選", preview)
        self.assertIn("i.ytimg.com/vi/abc123", preview)
        self.assertNotIn("github.com/owner.png", preview)
        self.assertIn("if(!section.querySelector('.image-card'))section.remove()", preview)

    def test_dashboard_prioritizes_local_urgent_then_stock_before_ai(self) -> None:
        now = datetime.now(timezone.utc)
        clusters = tuple(rank_items([
            IntelligenceItem("Codex 新功能", "https://example.com/ai", "Google News", now, category="AI／Codex"),
            IntelligenceItem("聯電重大公告", "https://example.com/stock", "Google News", now, category="股票與市場"),
            IntelligenceItem("台中火災封路", "https://example.com/local", "Google News", now, category="台中現在要注意"),
        ]))
        preview = HtmlPreviewRenderer().render(type("Report", (), {
            "generated_at": now, "clusters": clusters, "source_errors": (), "mode": "demo",
            "source_count": 1, "health_label": "來源正常", "health_note": "測試",
        })())
        self.assertLess(preview.index("<h1>台中火災封路</h1>"), preview.index("<h3>聯電重大公告</h3>"))
        self.assertIn('data-channel-link=', preview)
        self.assertIn('daily-intelligence-item-feedback-v2', preview)

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

    def test_profile_keeps_generic_github_trending_projects(self) -> None:
        profile = load_interest_profile()
        now = datetime.now(timezone.utc)
        repository = IntelligenceItem(
            "GitHub 今日熱門專案：some-owner/useful-tool",
            "https://github.com/some-owner/useful-tool",
            "GitHub Trending",
            now,
            category="GitHub",
        )
        self.assertTrue(profile.matches(repository))

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

    def test_google_news_keeps_good_results_when_one_query_is_malformed(self) -> None:
        """One broken RSS description must not wipe all other interest results."""
        profile = load_interest_profile()
        good_feed = """<?xml version='1.0'?><rss><channel><item><title>GTA 6 新消息</title><link>https://example.com/gta</link><pubDate>Fri, 11 Jul 2026 01:00:00 GMT</pubDate></item></channel></rss>"""
        calls = 0

        def fake_get_text(_: str) -> str:
            nonlocal calls
            calls += 1
            if calls == 1:
                raise ValueError("bad response")
            return good_feed

        with patch("app.sources.interest_news.get_text", side_effect=fake_get_text):
            items = InterestNewsSource(profile).fetch()

        self.assertTrue(items)
        self.assertIn("GTA 6 新消息", [item.title for item in items])

    def test_google_news_rotates_queries_without_dropping_profile_topics(self) -> None:
        first = InterestNewsSource._rotated_queries(("A", "B", "C", "D", "E", "F"), 0)
        next_hour = InterestNewsSource._rotated_queries(("A", "B", "C", "D", "E", "F"), 1)
        self.assertEqual(first, ["A", "B", "C", "D", "E"])
        self.assertEqual(next_hour, ["B", "C", "D", "E", "F"])

    def test_game_query_window_is_not_only_palworld(self) -> None:
        profile = load_interest_profile()
        games = next(category for category in profile.categories if category.name == "遊戲與電競")
        selected = InterestNewsSource._rotated_queries(games.queries, 0)
        joined = " ".join(selected).lower()
        self.assertIn("幻獸帕魯", joined)
        self.assertIn("gta", joined)
        self.assertIn("sf online", joined)
        self.assertIn("地平線", joined)
        self.assertIn("魔獸", joined)

    def test_dashboard_has_youth_and_sports_channels_with_three_demo_items(self) -> None:
        report = GenerateDailyReport([DemoSource()], load_interest_profile()).run("demo")
        preview = HtmlPreviewRenderer().render(report)
        self.assertIn("年輕人現在紅什麼", preview)
        self.assertIn("運動與 NBA", preview)
        self.assertIn("萊爾富桃子水", preview)
        self.assertIn("NBA 球員交易", preview)
        self.assertIn("挪威足球", preview)
        self.assertIn("browser-use/browser-use", preview)
        self.assertIn("unclecode/crawl4ai", preview)


if __name__ == "__main__":
    unittest.main()
