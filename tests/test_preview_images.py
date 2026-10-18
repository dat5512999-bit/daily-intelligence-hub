from __future__ import annotations

import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from app.domain.models import IntelligenceItem
from app.application.generate_daily_report import GenerateDailyReport
from app.sources.preview_images import _ImageMetaParser, _public_https, enrich_preview_images, publisher_image


class PreviewImageTests(unittest.TestCase):
    def item(self, title: str, category: str, url: str, source: str = "Google News", image: str = "") -> IntelligenceItem:
        return IntelligenceItem(title, url, source, datetime.now(timezone.utc), category=category, image_url=image)

    def test_reads_only_publisher_declared_open_graph_or_twitter_images(self) -> None:
        parser = _ImageMetaParser()
        parser.feed('<meta property="og:title" content="story"><meta property="og:image" content="https://cdn.example/story.jpg"><meta name="twitter:image" content="https://cdn.example/other.jpg">')
        self.assertEqual(parser.image, "https://cdn.example/story.jpg")

    def test_rejects_insecure_and_private_image_urls(self) -> None:
        self.assertFalse(_public_https("http://cdn.example/photo.jpg", resolve=False))
        self.assertFalse(_public_https("https://127.0.0.1/photo.jpg", resolve=False))
        self.assertFalse(_public_https("https://user:pass@cdn.example/photo.jpg", resolve=False))
        self.assertTrue(_public_https("https://cdn.example/photo.jpg", resolve=False))

    def test_only_scrapes_a_small_number_of_news_items_and_keeps_existing_images(self) -> None:
        items = [
            self.item("台中活動", "台中好康與活動", "https://news.google.com/rss/articles/one"),
            self.item("另一則台中", "台中好康與活動", "https://news.google.com/rss/articles/two"),
            self.item("動漫新作", "動漫與娛樂", "https://news.google.com/rss/articles/three"),
            self.item("已有 RSS 海報", "Netflix 新劇", "https://news.google.com/rss/articles/four", image="https://cdn.example/poster.jpg"),
            self.item("不抓社群頁", "生活流行", "https://www.reddit.com/r/example", "Reddit"),
        ]
        with patch("app.sources.preview_images.publisher_image", side_effect=lambda url: "https://cdn.example/preview.jpg") as fetch:
            result = enrich_preview_images(items, max_pages=2)
        self.assertEqual(fetch.call_count, 2)
        self.assertEqual(result[0].image_url, "https://cdn.example/preview.jpg")
        self.assertEqual(result[1].image_url, "")
        self.assertEqual(result[2].image_url, "https://cdn.example/preview.jpg")
        self.assertEqual(result[3].image_url, "https://cdn.example/poster.jpg")
        self.assertEqual(result[4].image_url, "")

    def test_does_not_fetch_non_google_article_or_invent_a_fallback(self) -> None:
        with patch("app.sources.preview_images.build_opener") as opener:
            self.assertEqual(publisher_image("https://example.com/article"), "")
            opener.assert_not_called()

    def test_only_live_report_attempts_optional_image_enrichment(self) -> None:
        class NewsSource:
            name = "Google News"

            def fetch(self):
                return [PreviewImageTests().item("台中展覽近期開展", "台中好康與活動", "https://news.google.com/rss/articles/one")]

        with patch("app.application.generate_daily_report.enrich_preview_images", side_effect=lambda items: items) as enrich:
            GenerateDailyReport([NewsSource()]).run("demo")
            enrich.assert_not_called()
            GenerateDailyReport([NewsSource()]).run("live")
            enrich.assert_called_once()


if __name__ == "__main__":
    unittest.main()
