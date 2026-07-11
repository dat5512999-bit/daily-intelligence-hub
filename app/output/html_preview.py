"""A self-contained, mobile-first personal intelligence console."""

from __future__ import annotations

from html import escape
from urllib.parse import quote

from app.domain.models import DailyReport, IntelligenceCluster


class HtmlPreviewRenderer:
    """Render information as a focused mission console, not a social-media feed."""

    _categories: tuple[tuple[str, str, str], ...] = (
        ("\u793e\u7fa4\u51b7\u9580\u96f7\u9054", "&#8981;", "#f2d35d"),
        ("\u641c\u5c0b\u8da8\u52e2", "&#8981;", "#4dd7ff"),
        ("\u77ed\u5f71\u97f3\u8da8\u52e2", "&#9835;", "#ff6b9f"),
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
        category = escape(cluster.category, quote=True)
        title = escape(cluster.title, quote=True)
        return (
            f'<article class="{style}" style="--accent:{accent}" data-category="{category}" data-title="{title}"><div class="mission-top">'
            f'<span class="mission-number">\u4efb\u52d9 {number:02d}</span><span class="mission-icon">{icon}</span></div>'
            f'<div class="mission-category">{escape(cluster.category)} &#183; {len(cluster.sources)} \u500b\u4f86\u6e90</div>'
            f'<h3>{escape(cluster.title)}</h3><p class="impact">{escape(cluster.attention_label)}</p>'
            f'<p class="summary"><b>30 \u79d2\u60c5\u5831\uff1a</b>{escape(cluster.summary)}</p>'
            f'<details><summary>\u5c55\u958b\u60c5\u5831\u5206\u6790</summary><p>{escape(cluster.why_it_appeared)}</p></details>'
            f'<div class="actions"><a class="button" href="{escape(cluster.primary_url, quote=True)}">\u9032\u5165\u60c5\u5831</a>'
            f'<a class="button ghost" href="{escape(translate_url, quote=True)}">\u7e41\u4e2d\u7ffb\u8b6f</a></div>'
            f'<div class="feedback"><button type="button" data-vote="more">\u591a\u770b\u9019\u985e</button><button type="button" data-vote="less">\u5c11\u770b\u9019\u985e</button></div>'
            f'<footer><span class="pulse"></span>{escape(cluster.signal_label)}</footer></article>'
        )

    def render(self, report: DailyReport) -> str:
        mode_label = "\u96e2\u7dda\u7bc4\u4f8b" if report.mode == "demo" else "\u5373\u6642\u9023\u7dda"
        source_count = len({source for cluster in report.clusters for source in cluster.sources})
        discovery_count = sum(1 for cluster in report.clusters if cluster.category in {"社群冷門雷達", "搜尋趨勢", "短影音趨勢"})
        stock_count = sum(1 for cluster in report.clusters if cluster.category == "股票與市場")
        metric_strip = (
            f'<div class="metrics"><div><b>{len(report.clusters)}</b><span>則情報</span></div>'
            f'<div><b>{discovery_count}</b><span>個苗頭</span></div>'
            f'<div><b>{stock_count}</b><span>則持股</span></div>'
            f'<div><b>{source_count}</b><span>個來源</span></div></div>'
        )
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
        return f'''<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>\u4eca\u5929\u7d05\u4ec0\u9ebc\u60c5\u5831\u96f7\u9054</title><style>:root{{color-scheme:dark}}*{{box-sizing:border-box}}body{{margin:0;background:#0b0e14;color:#f5f2ea;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}body:before{{content:"";position:fixed;inset:0;pointer-events:none;background:linear-gradient(135deg,#102538 0%,transparent 38%),linear-gradient(315deg,#3b1f35 0%,transparent 34%);z-index:-1}}main{{max-width:820px;margin:auto;padding:18px 14px 48px}}.console{{border:1px solid #2b3443;border-radius:8px;background:#101722e6;box-shadow:0 24px 70px #0009;overflow:hidden}}.console-header{{padding:24px;background:linear-gradient(120deg,#162334,#231b2b 55%,#2b2630);border-bottom:1px solid #3b4658}}.status{{display:flex;justify-content:space-between;gap:8px;color:#b6c0cf;font-size:.78rem;letter-spacing:.08em}}.online{{color:#75dfb4}}h1{{font-size:clamp(2rem,8vw,3.2rem);margin:14px 0 8px;letter-spacing:0;font-weight:850}}.console-header p{{margin:0;color:#d2d8e2}}.metrics{{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:18px}}.metrics div{{border:1px solid #414b5b;background:#ffffff0b;border-radius:8px;padding:10px}}.metrics b{{display:block;font-size:1.25rem;color:#fff}}.metrics span{{font-size:.76rem;color:#aeb8c7}}.system-warning{{margin:15px;padding:15px;border:1px solid #ff7b8d;border-radius:8px;background:#321b27;color:#ffdce2}}.primary-intro{{padding:20px 20px 4px}}.primary-intro small,.channel small{{color:#94a1b5;letter-spacing:.12em}}h2{{margin:5px 0;font-size:1.12rem}}.primary-intro p{{margin:0;color:#b8c1ce;line-height:1.55}}.mission-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(235px,1fr));gap:12px;padding:16px 20px 22px}}.mission{{position:relative;overflow:hidden;background:#151d2a;border:1px solid #2d394b;border-radius:8px;padding:16px;box-shadow:inset 4px 0 var(--accent)}}.mission.is-muted{{display:none}}.mission.is-loved{{border-color:var(--accent);box-shadow:inset 4px 0 var(--accent),0 0 0 1px color-mix(in srgb,var(--accent) 35%,transparent)}}.mission:after{{content:"";position:absolute;right:0;top:0;width:42%;height:3px;background:var(--accent);opacity:.85}}.featured{{background:linear-gradient(145deg,#1b2737,#151d2a);border-color:#4a5a72}}.mission-top{{display:flex;align-items:center;justify-content:space-between}}.mission-number{{font-size:.72rem;letter-spacing:.1em;color:#9eabba}}.mission-icon{{color:var(--accent);font-size:1.2rem}}.mission-category{{margin-top:12px;color:var(--accent);font-size:.8rem;font-weight:760}}h3{{font-size:1.08rem;line-height:1.45;margin:7px 0 9px;letter-spacing:0}}.impact{{display:inline-block;margin:0;padding:5px 8px;border:1px solid color-mix(in srgb,var(--accent) 55%,transparent);border-radius:8px;color:#f3f6fb;background:#ffffff0a;font-size:.82rem}}.summary{{color:#d6dde7;line-height:1.65;margin:11px 0}}details{{color:#aeb7c6;line-height:1.6}}summary{{cursor:pointer;color:#d7deeb;font-weight:650}}.actions,.feedback{{display:flex;gap:8px;margin:15px 0 10px;flex-wrap:wrap}}.feedback{{margin-top:4px}}.button,.feedback button{{display:inline-block;text-decoration:none;background:var(--accent);color:#09101d;padding:8px 10px;border-radius:8px;font-size:.84rem;font-weight:800;border:0;cursor:pointer}}.button.ghost,.feedback button{{background:#222c3c;color:#e5ebf5;border:1px solid #414d60}}.feedback button[data-vote="more"]{{border-color:color-mix(in srgb,var(--accent) 70%,#414d60)}}.feedback-note{{margin:0 20px 12px;color:#94a1b5;font-size:.82rem}}footer{{display:flex;align-items:center;gap:6px;padding-top:10px;border-top:1px solid #2c3748;color:#9eabba;font-size:.8rem}}.pulse{{width:7px;height:7px;border-radius:50%;background:var(--accent);box-shadow:0 0 10px var(--accent)}}.channel{{margin-top:1px;border-top:1px solid #2a3545}}.channel-title{{display:flex;gap:10px;align-items:center;padding:20px 20px 0}}.channel-title>span{{color:var(--accent);font-size:1.3rem}}.channel h2{{color:#fbfaf6}}.trust{{margin:0 20px 22px;padding:15px;border:1px solid #303b4d;border-radius:8px;background:#0d131d;color:#b8c1ce;line-height:1.6}}.trust h2{{color:#f5f2ea}}ul{{color:#ffabb9;margin-bottom:0}}@media(max-width:520px){{main{{padding:0}}.console{{border-radius:0;min-height:100vh}}.console-header{{padding:22px 17px}}.metrics{{grid-template-columns:repeat(2,1fr)}}.primary-intro{{padding:19px 17px 2px}}.mission-grid{{grid-template-columns:1fr;padding:14px 17px 20px}}.channel-title{{padding:18px 17px 0}}.trust{{margin:0 17px 22px}}}}</style></head><body><main><section class="console"><header class="console-header"><div class="status"><span>\u500b\u4eba\u8da8\u52e2\u63a7\u5236\u53f0</span><span class="online">&#9679; {mode_label}</span></div><h1>\u4eca\u5929\u7d05\u4ec0\u9ebc\uff1f</h1><p>{escape(report.generated_at.astimezone().strftime('%Y-%m-%d %H:%M %Z'))} &#183; \u65b0\u805e\u4fdd\u5e95\uff0c\u793e\u7fa4\u82d7\u982d\u512a\u5148\uff0c\u6301\u80a1\u96f7\u9054\u540c\u6b65\u770b</p>{metric_strip}</header>{empty}<section class="primary-intro"><small>\u6548\u7387\u6383\u63cf</small><h2>\u5148\u5224\u65b7\u4eca\u5929\u503c\u4e0d\u503c\u5f97\u6df1\u5165</h2><p>\u4e0a\u65b9\u5148\u770b\u6578\u91cf\u8207\u4f86\u6e90\uff0c\u4e0b\u65b9\u518d\u770b\u53ef\u80fd\u88ab\u554f\u5230\u7684\u4e8b\u3002</p></section><p class="feedback-note">\u6309\u300c\u591a\u770b\u9019\u985e\u300d\u6216\u300c\u5c11\u770b\u9019\u985e\u300d\u6703\u5148\u8a18\u5728\u9019\u53f0\u624b\u6a5f/\u700f\u89bd\u5668\uff0c\u5e6b\u4f60\u7576\u4e0b\u6e05\u7406\u7248\u9762\u3002</p><section class="mission-grid">{primary_cards}</section>{channels}<section class="trust"><h2>\u60c5\u5831\u5b89\u5168\u63d0\u793a</h2><p>\u793e\u7fa4\u8207\u641c\u5c0b\u8a0a\u865f\u53ea\u4ee3\u8868\u5927\u5bb6\u6b63\u5728\u597d\u5947\u6216\u8a0e\u8ad6\uff0c\u4e0d\u7b49\u65bc\u4e8b\u5be6\u3002\u80a1\u7968\u76f8\u95dc\u5167\u5bb9\u53ea\u662f\u60c5\u5831\u63d0\u9192\uff0c\u4e0d\u662f\u8cb7\u8ce3\u5efa\u8b70\u3002</p>{'<ul>'+warnings+'</ul>' if warnings else ''}</section></section></main><script>const key='daily-intelligence-feedback-v1';const data=JSON.parse(localStorage.getItem(key)||'{{"more":[],"less":[]}}');function save(){{localStorage.setItem(key,JSON.stringify(data));}}function applyFeedback(){{document.querySelectorAll('.mission').forEach(card=>{{const category=card.dataset.category||'';card.classList.toggle('is-muted',data.less.includes(category));card.classList.toggle('is-loved',data.more.includes(category));}});}}document.querySelectorAll('.feedback button').forEach(button=>button.addEventListener('click',()=>{{const card=button.closest('.mission');const category=card.dataset.category||'';const list=button.dataset.vote==='more'?data.more:data.less;const other=button.dataset.vote==='more'?data.less:data.more;if(!list.includes(category))list.push(category);const index=other.indexOf(category);if(index>=0)other.splice(index,1);save();applyFeedback();}}));applyFeedback();</script></body></html>'''
