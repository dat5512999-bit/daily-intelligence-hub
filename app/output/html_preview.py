"""A self-contained, mobile-first personal intelligence console."""

from __future__ import annotations

from html import escape
from urllib.parse import quote

from app.domain.models import DailyReport, IntelligenceCluster


class HtmlPreviewRenderer:
    """Render information as a focused mission console, not a social-media feed."""

    _categories: tuple[tuple[str, str, str], ...] = (
        ("\u53f0\u4e2d\u73fe\u5728\u8981\u6ce8\u610f", "&#9888;", "#ff5d73"),
        ("AI\uff0fCodex", "&#9670;", "#8f7cff"),
        ("\u904a\u6232\u8207\u96fb\u7af6", "&#9654;", "#38d6a5"),
        ("\u52d5\u6f2b\u8207\u5a1b\u6a02", "&#9733;", "#f5aa4b"),
        ("\u80a1\u7968\u8207\u5e02\u5834", "&#8599;", "#46b9ff"),
        ("\u53f0\u4e2d\u597d\u5eb7\u8207\u6d3b\u52d5", "&#10022;", "#ff7ac6"),
    )

    @staticmethod
    def _translation_url(url: str) -> str:
        return f"https://translate.google.com/translate?sl=auto&tl=zh-TW&u={quote(url, safe='')}"

    def _style_for(self, category: str) -> tuple[str, str]:
        for name, icon, accent in self._categories:
            if name == category:
                return icon, accent
        return "&#9679;", "#7184a8"

    def _mission_card(self, cluster: IntelligenceCluster, number: int, featured: bool = False) -> str:
        icon, accent = self._style_for(cluster.category)
        translate_url = self._translation_url(cluster.primary_url)
        style = "mission featured" if featured else "mission"
        return (
            f'<article class="{style}" style="--accent:{accent}"><div class="mission-top">'
            f'<span class="mission-number">\u4efb\u52d9 {number:02d}</span><span class="mission-icon">{icon}</span></div>'
            f'<div class="mission-category">{escape(cluster.category)} &#183; {len(cluster.sources)} \u500b\u4f86\u6e90</div>'
            f'<h3>{escape(cluster.title)}</h3><p class="impact">{escape(cluster.attention_label)}</p>'
            f'<p class="summary"><b>30 \u79d2\u60c5\u5831\uff1a</b>{escape(cluster.summary)}</p>'
            f'<details><summary>\u5c55\u958b\u60c5\u5831\u5206\u6790</summary><p>{escape(cluster.why_it_appeared)}</p></details>'
            f'<div class="actions"><a class="button" href="{escape(cluster.primary_url, quote=True)}">\u9032\u5165\u60c5\u5831</a>'
            f'<a class="button ghost" href="{escape(translate_url, quote=True)}">\u7e41\u4e2d\u7ffb\u8b6f</a></div>'
            f'<footer><span class="pulse"></span>{escape(cluster.signal_label)}</footer></article>'
        )

    def render(self, report: DailyReport) -> str:
        mode_label = "\u96e2\u7dda\u7bc4\u4f8b" if report.mode == "demo" else "\u5373\u6642\u9023\u7dda"
        primary_cards = "".join(self._mission_card(cluster, index, True) for index, cluster in enumerate(report.clusters[:3], 1))
        remaining = report.clusters[3:]
        channels = ""
        for category, icon, accent in self._categories:
            filtered = [cluster for cluster in remaining if cluster.category == category]
            if filtered:
                cards = "".join(self._mission_card(cluster, index + 4) for index, cluster in enumerate(filtered))
                channels += f'<section class="channel" style="--accent:{accent}"><div class="channel-title"><span>{icon}</span><div><small>\u60c5\u5831\u983b\u9053</small><h2>{escape(category)}</h2></div></div><div class="mission-grid">{cards}</div></section>'
        warnings = "".join(f"<li>{escape(error)}</li>" for error in report.source_errors)
        empty = (
            '<section class="system-warning"><b>\u7cfb\u7d71\u63d0\u793a</b><p>\u76ee\u524d\u7121\u6cd5\u53d6\u5f97\u5373\u6642\u60c5\u5831\u3002\u8acb\u78ba\u8a8d\u7db2\u8def\u5f8c\u518d\u57f7\u884c\u4e00\u6b21\uff1b\u7cfb\u7d71\u4e0d\u6703\u7528\u7bc4\u4f8b\u8cc7\u6599\u5192\u5145\u771f\u5be6\u8da8\u52e2\u3002</p></section>'
            if not report.clusters else ""
        )
        return f'''<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>\u6211\u7684\u60c5\u5831\u63a7\u5236\u53f0</title><style>:root{{color-scheme:dark}}*{{box-sizing:border-box}}body{{margin:0;background:#070b13;color:#edf2ff;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}body:before{{content:"";position:fixed;inset:0;pointer-events:none;background:linear-gradient(115deg,#12204155,transparent 42%),radial-gradient(circle at 85% 5%,#8f7cff22,transparent 28%);z-index:-1}}main{{max-width:780px;margin:auto;padding:16px 13px 48px}}.console{{border:1px solid #273653;border-radius:20px;background:#0d1423cc;box-shadow:0 22px 70px #0008;overflow:hidden}}.console-header{{padding:22px;background:linear-gradient(120deg,#101b31,#17284a);border-bottom:1px solid #31466d}}.status{{display:flex;justify-content:space-between;gap:8px;color:#a9b9d7;font-size:.78rem;letter-spacing:.08em}}.online{{color:#4be1a8}}h1{{font-size:clamp(1.9rem,8vw,3rem);margin:13px 0 6px;letter-spacing:.02em}}.console-header p{{margin:0;color:#b7c6e1}}.system-warning{{margin:15px;padding:15px;border:1px solid #ff7b8d;border-radius:12px;background:#321b27;color:#ffdce2}}.primary-intro{{padding:20px 20px 4px}}.primary-intro small,.channel small{{color:#7184a8;letter-spacing:.12em}}h2{{margin:5px 0;font-size:1.12rem}}.primary-intro p{{margin:0;color:#aebbd1;line-height:1.55}}.mission-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(235px,1fr));gap:11px;padding:16px 20px 22px}}.mission{{position:relative;overflow:hidden;background:#121b2c;border:1px solid #263653;border-radius:14px;padding:16px;box-shadow:inset 3px 0 var(--accent)}}.mission:after{{content:"";position:absolute;right:-36px;top:-36px;width:100px;height:100px;border:1px solid var(--accent);border-radius:50%;opacity:.2}}.featured{{background:linear-gradient(145deg,#172441,#111a2b);border-color:#405b89}}.mission-top{{display:flex;align-items:center;justify-content:space-between}}.mission-number{{font-size:.72rem;letter-spacing:.1em;color:#91a4c6}}.mission-icon{{color:var(--accent);font-size:1.2rem}}.mission-category{{margin-top:12px;color:var(--accent);font-size:.8rem;font-weight:700}}h3{{font-size:1.1rem;line-height:1.45;margin:7px 0 9px}}.impact{{display:inline-block;margin:0;padding:5px 8px;border:1px solid color-mix(in srgb,var(--accent) 60%,transparent);border-radius:7px;color:#dbe6ff;background:#ffffff08;font-size:.82rem}}.summary{{color:#d1daeb;line-height:1.65;margin:11px 0}}details{{color:#9fadc5;line-height:1.6}}summary{{cursor:pointer;color:#bdcaf0;font-weight:650}}.actions{{display:flex;gap:8px;margin:15px 0 10px}}.button{{display:inline-block;text-decoration:none;background:var(--accent);color:#09101d;padding:8px 10px;border-radius:8px;font-size:.84rem;font-weight:750}}.button.ghost{{background:#202c43;color:#d6e2fa;border:1px solid #3b4c6b}}footer{{display:flex;align-items:center;gap:6px;padding-top:10px;border-top:1px solid #25334d;color:#8ea0be;font-size:.8rem}}.pulse{{width:7px;height:7px;border-radius:50%;background:var(--accent);box-shadow:0 0 10px var(--accent)}}.channel{{margin-top:1px;border-top:1px solid #24324b}}.channel-title{{display:flex;gap:10px;align-items:center;padding:20px 20px 0}}.channel-title>span{{color:var(--accent);font-size:1.3rem}}.channel h2{{color:#f1f5ff}}.trust{{margin:0 20px 22px;padding:15px;border:1px solid #293957;border-radius:12px;background:#0a101c;color:#aebbd1;line-height:1.6}}.trust h2{{color:#e9effc}}ul{{color:#ff9dac;margin-bottom:0}}@media(max-width:520px){{main{{padding:0}}.console{{border-radius:0;min-height:100vh}}.console-header{{padding:21px 17px}}.primary-intro{{padding:19px 17px 2px}}.mission-grid{{grid-template-columns:1fr;padding:14px 17px 20px}}.channel-title{{padding:18px 17px 0}}.trust{{margin:0 17px 22px}}}}</style></head><body><main><section class="console"><header class="console-header"><div class="status"><span>\u500b\u4eba\u60c5\u5831\u63a7\u5236\u53f0</span><span class="online">&#9679; {mode_label}</span></div><h1>\u4eca\u65e5\u4efb\u52d9\uff1a\u638c\u63e1\u91cd\u9ede</h1><p>{escape(report.generated_at.astimezone().strftime('%Y-%m-%d %H:%M %Z'))} &#183; \u5148\u5b8c\u6210 3 \u500b\u5fc5\u770b\u60c5\u5831</p></header>{empty}<section class="primary-intro"><small>\u4e3b\u8981\u4efb\u52d9</small><h2>\u4eca\u65e5\u5fc5\u770b</h2><p>\u4e0d\u9700\u8981\u6ed1\u4e00\u5806\u65b0\u805e\uff0c\u5148\u770b\u9019 3 \u4ef6\u5c31\u597d\u3002</p></section><section class="mission-grid">{primary_cards}</section>{channels}<section class="trust"><h2>\u60c5\u5831\u5b89\u5168\u63d0\u793a</h2><p>\u793e\u7fa4\u71b1\u5ea6\u53ea\u4ee3\u8868\u5927\u5bb6\u5728\u8a0e\u8ad6\u3002\u9047\u5230\u91d1\u9322\u3001\u5b89\u5168\u6216\u91cd\u5927\u4e8b\u4ef6\uff0c\u8acb\u518d\u9032\u5165\u60c5\u5831\uff0c\u78ba\u8a8d\u5b98\u65b9\u516c\u544a\u6216\u53ef\u9760\u5a92\u9ad4\u3002</p>{'<ul>'+warnings+'</ul>' if warnings else ''}</section></section></main></body></html>'''
