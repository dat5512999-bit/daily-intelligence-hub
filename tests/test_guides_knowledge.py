"""Acceptance checks for understandable repo guides and attributed daily facts."""

import unittest
from dataclasses import replace
from datetime import date

from app.analyzer.github_guide import repository_guide
from app.analyzer.ranking import rank_items
from app.application.generate_daily_report import GenerateDailyReport
from app.domain.models import DailyReport, IntelligenceItem
from app.infrastructure.interests import load_interest_profile
from app.output.html_preview import HtmlPreviewRenderer
from app.output.markdown import MarkdownRenderer
from app.sources.knowledge import FACTS, REVIEWED_AT, KnowledgeSource
from app.sources.daily_boost import IDEAS, DailyBoostSource
from app.infrastructure.report_state import article_key


class GuideKnowledgeTests(unittest.TestCase):
    def item(self, description: str = "") -> IntelligenceItem:
        return IntelligenceItem("GitHub 今日熱門專案：owner/coding-agent", "https://github.com/owner/coding-agent",
                                "GitHub Trending", REVIEWED_AT, category="GitHub", repo_description=description)

    def test_repo_name_is_not_evidence_of_capability(self) -> None:
        guide = repository_guide(rank_items([self.item()])[0])
        self.assertFalse(guide.matched)
        self.assertEqual(guide.steps, ())

    def test_specific_evidence_has_chinese_example_and_concept_flow(self) -> None:
        cluster = rank_items([self.item("An automated testing tool for end-to-end website tests")])[0]
        guide = repository_guide(cluster)
        self.assertTrue(guide.matched)
        self.assertIn("檢查", guide.purpose)
        row = HtmlPreviewRenderer()._compact_row(cluster, 1, "test")
        for label in ("用在哪裡", "使用例子", "上手門檻", "不是實際介面", "官方說明翻成繁中"):
            self.assertIn(label, row)
        self.assertNotIn("<img", row)

    def test_cloud_trending_types_have_honest_guides(self) -> None:
        descriptions = ("Reverse engineer anything with agents, from app behavior down to native binaries.",
                        "Tool for automatic PS5 executables porting to Linux and Windows")
        for description in descriptions:
            guide = repository_guide(rank_items([self.item(description)])[0])
            self.assertTrue(guide.matched)
            self.assertEqual(len(guide.steps), 3)
            self.assertIn("工程師", guide.audience)

    def test_evidence_is_escaped_and_not_a_free_usage_promise(self) -> None:
        cluster = rank_items([self.item('coding assistant <script>alert(1)</script>')])[0]
        row = HtmlPreviewRenderer()._briefing(cluster)
        self.assertNotIn("<script>", row)
        self.assertIn("&lt;script&gt;", row)
        self.assertIn("不代表免", row)

    def test_daily_facts_are_three_distinct_and_day_stable(self) -> None:
        today = KnowledgeSource(date(2026, 10, 7)).fetch()
        self.assertEqual(today, KnowledgeSource(date(2026, 10, 7)).fetch())
        self.assertEqual(len({item.url for item in today}), 3)
        self.assertNotEqual(today, KnowledgeSource(date(2026, 10, 8)).fetch())
        self.assertTrue(all(item.published_at == REVIEWED_AT for item in today))
        self.assertEqual(len(FACTS), 6)

    def test_knowledge_is_not_filtered_by_news_interest_profile(self) -> None:
        report = GenerateDailyReport([KnowledgeSource()], load_interest_profile()).run("demo")
        self.assertEqual(len(report.clusters), 3)
        self.assertEqual(report.source_count, 0, "Offline facts cannot mask a live-source outage")
        html = HtmlPreviewRenderer().render(report)
        self.assertIn("冷知識 · 每天三則", html)
        self.assertIn("3／3 則", html)
        self.assertNotIn('class="hero"', html)
        self.assertIn("非即時新聞", html)
        self.assertIn("冷知識 · 每天三則", MarkdownRenderer().render(report))

    def test_knowledge_count_stays_three_with_all_demo_channels(self) -> None:
        from app.infrastructure.demo_data import DemoSource
        report = GenerateDailyReport([DemoSource(), KnowledgeSource()], load_interest_profile()).run("demo")
        self.assertEqual(sum(cluster.category == "冷知識" for cluster in report.clusters), 3)
        self.assertEqual(sum(cluster.category == "GitHub" for cluster in report.clusters), 3)

    def test_daily_boost_has_three_original_actionable_ideas_and_is_day_stable(self) -> None:
        today = DailyBoostSource(date(2026, 10, 18)).fetch()
        self.assertEqual(len(today), 3)
        self.assertEqual(today, DailyBoostSource(date(2026, 10, 18)).fetch())
        self.assertNotEqual(today, DailyBoostSource(date(2026, 10, 19)).fetch())
        self.assertEqual([item.title for item in today], [item.title for item in DailyBoostSource(date(2026, 10, 25)).fetch()])
        self.assertEqual(len(IDEAS), 21, "Seven days of three ideas reduce immediate repetition")
        self.assertTrue(all(item.category == "每日充電" for item in today))
        self.assertTrue(all("今天試試：" in item.summary for item in today))
        self.assertEqual(len({article_key(cluster) for cluster in rank_items(today)}), 3)
        self.assertIn("把在意的事說清楚", " ".join(title for title, _, _ in IDEAS))

    def test_daily_boost_is_not_a_live_news_source_or_top_pick(self) -> None:
        report = GenerateDailyReport([DailyBoostSource(date(2026, 10, 18))], load_interest_profile()).run("demo")
        self.assertEqual(len(report.clusters), 3)
        self.assertEqual(report.source_count, 0)
        html = HtmlPreviewRenderer().render(report)
        self.assertIn("每日充電 · 30 秒", html)
        self.assertIn("原創小提醒", html)
        self.assertIn("今天試試：", html)
        self.assertIn("收藏這個提醒", html)
        self.assertNotIn("daily-idea://", html)
        self.assertNotIn('class="hero"', html)
        markdown = MarkdownRenderer().render(report)
        self.assertIn("每日充電 · 30 秒", markdown)
        self.assertIn("不是名人語錄或心理諮商", markdown)

    def test_watch_platforms_have_three_separate_query_categories(self) -> None:
        profile = load_interest_profile()
        expected = {"新番動漫", "Netflix 新劇", "Disney+ 新劇"}
        actual = {category.name for category in profile.categories}
        self.assertTrue(expected.issubset(actual))
        for name in expected:
            category = next(category for category in profile.categories if category.name == name)
            self.assertTrue(category.queries)


if __name__ == "__main__":
    unittest.main()
