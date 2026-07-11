"""Daily Intelligence Research Hub entry point."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from app.application.generate_daily_report import GenerateDailyReport
from app.infrastructure.demo_data import DemoSource
from app.infrastructure.interests import load_interest_profile
from app.output.html_preview import HtmlPreviewRenderer
from app.output.markdown import MarkdownRenderer
from app.output.assets import APP_ICON_SVG, WEB_MANIFEST
from app.sources.github import GitHubTrendingSource
from app.sources.hackernews import HackerNewsSource
from app.sources.interest_news import InterestNewsSource
from app.sources.reddit import RedditSource
from app.sources.dcard import DcardSource
from app.sources.tiktok import TikTokTrendsSource
from app.sources.taiwan_events import TaiwanTourismEventsSource
from app.sources.trends import GoogleTrendsSource
from app.sources.youtube import YouTubeSource


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a daily intelligence report.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--demo", action="store_true", help="Use built-in data without network access.")
    mode.add_argument("--live", action="store_true", help="Fetch current public source data.")
    parser.add_argument("--output-dir", type=Path, default=Path("reports"), help="Report directory.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    profile = load_interest_profile()
    sources = [DemoSource()] if args.demo else [InterestNewsSource(profile), TaiwanTourismEventsSource(), GitHubTrendingSource(), RedditSource(), HackerNewsSource(), YouTubeSource(), DcardSource(), GoogleTrendsSource(), TikTokTrendsSource()]
    report = GenerateDailyReport(sources, profile).run(mode="demo" if args.demo else "live")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    markdown_path = args.output_dir / "Daily_Report.md"
    preview_path = args.output_dir / "preview.html"
    index_path = args.output_dir / "index.html"
    icon_path = args.output_dir / "app-icon.svg"
    manifest_path = args.output_dir / "manifest.webmanifest"
    markdown_path.write_text(MarkdownRenderer().render(report), encoding="utf-8")
    html = HtmlPreviewRenderer().render(report)
    preview_path.write_text(html, encoding="utf-8")
    # GitHub Pages 的首頁固定讀取 index.html；同時保留 preview.html，方便在電腦上雙擊開啟。
    index_path.write_text(html, encoding="utf-8")
    icon_path.write_text(APP_ICON_SVG, encoding="utf-8")
    manifest_path.write_text(WEB_MANIFEST, encoding="utf-8")
    print(f"報告已建立：{markdown_path.resolve()}")
    print(f"預覽已建立：{preview_path.resolve()}")
    if report.source_errors:
        print("部分來源暫時無法取得資料：" + "；".join(report.source_errors))
    return 0


if __name__ == "__main__":
    sys.exit(main())
