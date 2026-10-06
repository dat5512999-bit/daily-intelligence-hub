"""Acceptance checks for evidence and honest cross-run update status."""

import unittest
from datetime import datetime, timedelta, timezone
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory

from app.analyzer.ranking import rank_items
from app.analyzer.summary import summarize
from app.analyzer.topics import topic_for
from app.domain.models import DailyReport, IntelligenceItem
from app.infrastructure.report_state import compare_report, load_snapshot, save_snapshot
from app.output.html_preview import HtmlPreviewRenderer
from unittest.mock import patch
from app.sources.github import GitHubTrendingSource


class QualityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.now = datetime.now(timezone.utc)
        self.item = IntelligenceItem("Codex 更新功能", "https://example.com/a", "Google News", self.now,
                                     "這則消息符合你關注的 AI。開啟原文可確認。", category="AI／Codex")
        self.report = DailyReport(generated_at=self.now, clusters=tuple(rank_items([self.item])))

    def test_boilerplate_is_never_presented_as_read_article(self) -> None:
        self.assertTrue(summarize((self.item,)).startswith("僅取得標題"))
        real = replace(self.item, summary="新版加入離線搜尋模式，使用者可搜尋已下載的專案。")
        self.assertIn("離線搜尋模式", summarize((self.item, real)))

    def test_first_run_and_same_content_do_not_claim_new_items(self) -> None:
        first, state = compare_report(self.report, {})
        self.assertFalse(first.comparison_available)
        self.assertIsNone(first.last_content_change_at)
        later, _ = compare_report(replace(self.report, generated_at=self.now + timedelta(hours=1)), state)
        self.assertTrue(later.comparison_available)
        self.assertEqual(later.new_item_count, 0)
        self.assertEqual(later.changed_item_count, 0)
        self.assertIsNone(later.last_content_change_at)

    def test_new_and_revised_content_are_counted_separately(self) -> None:
        _, state = compare_report(self.report, {})
        revised = replace(self.report.clusters[0], summary="來源補上新功能操作說明。")
        new = rank_items([replace(self.item, url="https://example.com/b", title="另一個專案的新消息")])[0]
        result, _ = compare_report(replace(self.report, clusters=(revised, new)), state)
        self.assertEqual((result.new_item_count, result.changed_item_count), (1, 1))
        self.assertEqual(result.last_content_change_at, self.now)

    def test_outage_and_returning_items_keep_comparison_history(self) -> None:
        _, state = compare_report(self.report, {})
        empty, outage_state = compare_report(replace(self.report, clusters=()), state)
        self.assertEqual(empty.new_item_count, 0)
        returned, _ = compare_report(self.report, outage_state)
        self.assertEqual(returned.new_item_count, 0)

    def test_invalid_snapshot_cannot_break_report(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            path.write_text("{broken", encoding="utf-8")
            self.assertEqual(load_snapshot(path), {})
            report, state = compare_report(self.report, {"schema": 1, "fingerprints": []})
            self.assertFalse(report.comparison_available)
            save_snapshot(path, state)
            self.assertEqual(load_snapshot(path), state)

    def test_topic_feedback_does_not_infer_entire_category(self) -> None:
        self.assertEqual(topic_for("幻獸帕魯重大更新"), "幻獸帕魯")
        self.assertEqual(topic_for("GTA 上市日期"), "GTA")
        self.assertEqual(topic_for("某個沒有具體名稱的遊戲更新"), "")
        row = HtmlPreviewRenderer()._compact_row(self.report.clusters[0], 1, "test")
        self.assertIn('data-topic="Codex"', row)
        self.assertIn("多看「Codex」", row)
        self.assertNotIn("多看「AI／Codex」", row)

    def test_page_states_schedule_is_not_a_completion_promise(self) -> None:
        html = HtmlPreviewRenderer().render(self.report)
        self.assertIn("最後檢查", html)
        self.assertIn("尚未建立可比較紀錄", html)
        self.assertIn("下次排程時段", html)
        self.assertIn("可能延遲", html)
        self.assertNotIn("預計下次", html)
        self.assertNotIn('class="hero-mark"', html)

    def test_github_trending_ignores_navigation_links(self) -> None:
        html = '<a href="/sponsors/explore">Sponsors</a><a href="/trending/developers">Developers</a>'
        html += ''.join(f'<article class="Box-row"><h2><a href="/owner/repo{number}">Repo</a></h2><p>真正的專案用途介紹</p></article>' for number in range(3))
        with patch("app.sources.github.get_text", return_value=html):
            items = GitHubTrendingSource().fetch()
        self.assertEqual(len(items), 3)
        self.assertTrue(all(item.url.startswith("https://github.com/owner/repo") for item in items))
        self.assertTrue(all(item.summary == "真正的專案用途介紹" for item in items))


if __name__ == "__main__":
    unittest.main()
