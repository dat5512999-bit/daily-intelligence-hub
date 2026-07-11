"""Markdown report renderer."""

from __future__ import annotations

from collections import defaultdict
from urllib.parse import quote

from app.domain.models import DailyReport
from app.output.time_format import format_taiwan_time


class MarkdownRenderer:
    @staticmethod
    def _translation_url(url: str) -> str:
        """Open the source through Google Translate without an API key."""
        return f"https://translate.google.com/translate?sl=auto&tl=zh-TW&u={quote(url, safe='')}"

    def render(self, report: DailyReport) -> str:
        stock_count = sum(1 for cluster in report.clusters if cluster.category == "股票與市場")
        lines = ["# 今天紅什麼情報雷達", "", f"更新時間：{format_taiwan_time(report.generated_at)}", f"模式：{report.mode}", f"資料狀態：{report.health_label}（{report.health_note}）", f"持股雷達：{stock_count} 則", "", "## 今天先看這三件事", ""]
        for index, cluster in enumerate(report.clusters[:3], 1):
            lines.extend([f"### {index}. {cluster.title}", f"建議：{cluster.decision_label}", f"你可能會在意：{cluster.attention_label}", f"白話重點：{cluster.summary}", f"{cluster.source_type_label} ｜ {cluster.signal_label} ｜ {cluster.why_it_appeared}", f"[看原文]({cluster.primary_url}) ｜ [翻成繁中閱讀]({self._translation_url(cluster.primary_url)})", ""])
        discovery = [cluster for cluster in report.clusters if cluster.category in {"社群冷門雷達", "搜尋趨勢", "短影音趨勢"} or cluster.signal_label in {"社群正在討論", "很多人正在搜尋"}]
        if discovery:
            lines.extend(["## 現在紅什麼／冷門苗頭", "這一區偏社群與搜尋訊號，可能比新聞更早出現，但也比較需要查證。", ""])
            for index, cluster in enumerate(discovery[:5], 1):
                lines.extend([f"### {index}. {cluster.title}", f"建議：{cluster.decision_label}", f"你可能會在意：{cluster.attention_label}", f"白話重點：{cluster.summary}", f"來源：{'、'.join(cluster.sources)} ｜ {cluster.source_type_label} ｜ {cluster.signal_label}", f"[看原文]({cluster.primary_url}) ｜ [翻成繁中閱讀]({self._translation_url(cluster.primary_url)})", ""])
        lines.extend(["## 新聞與其他趨勢（有空再看）", ""])
        for index, cluster in enumerate(report.clusters, 1):
            lines.extend([f"### {index}. {cluster.title}", f"建議：{cluster.decision_label}", f"你可能會在意：{cluster.attention_label}", f"白話重點：{cluster.summary}", f"來源：{'、'.join(cluster.sources)} ｜ {cluster.source_type_label} ｜ {cluster.signal_label}", f"[看原文]({cluster.primary_url}) ｜ [翻成繁中閱讀]({self._translation_url(cluster.primary_url)})", ""])
        categories: dict[str, list[str]] = defaultdict(list)
        for cluster in report.clusters:
            categories[cluster.category].append(f"- [{cluster.title}]({cluster.primary_url})")
        for category in ("社群冷門雷達", "搜尋趨勢", "短影音趨勢", "AI／Codex", "遊戲與電競", "動漫與娛樂", "台中現在要注意", "台中好康與活動", "股票與市場", "AI", "GitHub", "科技", "商業", "全球重要事件", "健康生活", "美食生活", "旅遊生活", "娛樂文化", "影音生活", "生活話題", "職場生活", "Dcard 熱門"):
            if categories[category]:
                lines.extend([f"## {category}", *categories[category], ""])
        if report.clusters:
            top = report.clusters[0]
            lines.extend(["## 今日最值得研究", f"[{top.title}]({top.primary_url})", top.summary, ""])
        unverified = [cluster for cluster in report.clusters if cluster.signal_label == "社群正在討論"]
        if unverified:
            lines.extend(["## 流行但先別急著相信", "以下內容反映社群熱度，不代表事件已被證實。", *[f"- [{cluster.title}]({cluster.primary_url})" for cluster in unverified], ""])
        if report.source_errors:
            lines.extend(["## 來源警示", *[f"- {error}" for error in report.source_errors], ""])
        if not report.clusters:
            lines.extend(["## 目前無法取得即時資料", "請確認網路連線後再執行一次。系統沒有用範例資料冒充即時趨勢。", ""])
        lines.append("閱讀設計：先看三件事，再決定是否閱讀其他趨勢；目標 3–5 分鐘完成。")
        return "\n".join(lines) + "\n"
