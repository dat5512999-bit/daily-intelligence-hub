"""Chinese, mobile-first output for the personal intelligence dashboard."""

from __future__ import annotations

from datetime import timedelta
from html import escape
from urllib.parse import quote

from app.domain.models import DailyReport, IntelligenceCluster
from app.output.time_format import format_taiwan_time


class HtmlPreviewRenderer:
    """A short daily briefing first; expandable interest channels second."""

    CHANNELS = (
        ("AI／Codex", "🤖", "AI／Codex"),
        ("遊戲與電競", "🎮", "遊戲與電競"),
        ("動漫與娛樂", "✨", "動漫與娛樂"),
        ("股票與市場", "📈", "你的持股雷達"),
        ("台中現在要注意", "📍", "台中現在要注意"),
        ("台中好康與活動", "🎫", "台中活動與好康"),
        ("生活流行", "☕", "生活流行"),
        ("GitHub", "⌘", "GitHub 熱門"),
    )

    @staticmethod
    def _translate(url: str) -> str:
        return f"https://translate.google.com/translate?sl=auto&tl=zh-TW&u={quote(url, safe='')}"

    @staticmethod
    def _link(cluster: IntelligenceCluster, label: str = "看原文") -> str:
        return f'<a class="text-link" href="{escape(cluster.primary_url, quote=True)}">{label} ↗</a>'

    @staticmethod
    def _item_id(cluster: IntelligenceCluster, index: int, area: str) -> str:
        return escape(f"{area}:{index}:{cluster.primary_url}", quote=True)

    @staticmethod
    def _is_chinese_readable(cluster: IntelligenceCluster) -> bool:
        return sum("\u4e00" <= char <= "\u9fff" for char in cluster.title) >= 2

    @staticmethod
    def _priority(cluster: IntelligenceCluster) -> tuple[int, float]:
        """Urgent local events and watched stocks outrank a normal AI update."""
        if cluster.decision_label.startswith("現在看") and cluster.category == "台中現在要注意":
            return (0, -cluster.score)
        if cluster.category == "股票與市場" and cluster.decision_label.startswith("現在看"):
            return (1, -cluster.score)
        if cluster.category == "AI／Codex":
            return (2, -cluster.score)
        return (3, -cluster.score)

    def _compact_row(self, cluster: IntelligenceCluster, index: int, area: str) -> str:
        item_id = self._item_id(cluster, index, area)
        category = escape(cluster.category, quote=True)
        return (
            f'<article class="compact" data-item="{item_id}" data-category="{category}"><div><span class="source-pill">{escape(cluster.source_type_label)}</span>'
            f'<h3>{escape(cluster.title)}</h3><p>{escape(cluster.decision_label)} · {escape(cluster.summary)}</p></div>'
            f'<div class="compact-actions">{self._link(cluster)}<button data-vote="more">👍 有興趣</button><button data-vote="less">🙈 少一點</button></div></article>'
        )

    def _hero(self, cluster: IntelligenceCluster) -> str:
        return (
            '<section class="hero"><div><span class="eyebrow">今天最值得先看</span>'
            f'<h1>{escape(cluster.title)}</h1><p class="decision">{escape(cluster.decision_label)}</p>'
            f'<p>{escape(cluster.summary)}</p><div class="hero-actions">{self._link(cluster, "進入情報")} '
            f'<a class="text-link muted" href="{escape(self._translate(cluster.primary_url), quote=True)}">翻成繁中</a></div></div>'
            '<div class="hero-mark" aria-hidden="true">✦</div></section>'
        )

    def _channel(self, category: str, icon: str, label: str, clusters: list[IntelligenceCluster]) -> str:
        identifier = quote(category, safe="")
        items = [cluster for cluster in clusters if cluster.category == category][:3]
        content = "".join(self._compact_row(cluster, index, f"channel-{identifier}") for index, cluster in enumerate(items, 1))
        if not content:
            content = '<p class="no-data">這一輪暫時沒有可靠的新消息；下一次更新會再找，不用硬塞不相關內容。</p>'
        return (
            f'<details class="channel" id="{identifier}"><summary><span>{icon}</span><b>{label}</b><small>{len(items)}／3 則</small></summary>'
            f'<div class="channel-body">{content}</div></details>'
        )

    def render(self, report: DailyReport) -> str:
        clusters = [cluster for cluster in report.clusters if self._is_chinese_readable(cluster)]
        picks = sorted(clusters, key=self._priority)[:3]
        hero = picks[0] if picks else None
        other_picks = picks[1:]
        trends = [cluster for cluster in clusters if cluster.source_type_label in {"搜尋熱度", "社群討論"} and cluster not in picks][:3]
        visuals = [cluster for cluster in clusters if cluster.image_url][:2]
        warning_html = "".join(f"<li>{escape(error)}</li>" for error in report.source_errors)
        pick_html = "".join(self._compact_row(cluster, index, "today") for index, cluster in enumerate(other_picks, 2))
        trend_html = "".join(f'<li><b>{index}</b><span>{escape(cluster.title)}</span>{self._link(cluster)}</li>' for index, cluster in enumerate(trends, 1))
        visual_html = "".join(
            f'<article class="image-card"><img loading="lazy" src="{escape(cluster.image_url, quote=True)}" alt="" '
            'onerror="const card=this.closest(\'article\');const section=this.closest(\'.visuals\');card.remove();if(!section.querySelector(\'.image-card\'))section.remove();">'
            f'<div><span class="source-pill">YouTube 影片</span><h3>{escape(cluster.title)}</h3>{self._link(cluster)}</div></article>'
            for cluster in visuals
        )
        channels = "".join(self._channel(category, icon, label, clusters) for category, icon, label in self.CHANNELS)
        shortcuts = "".join(f'<a href="#{quote(category, safe="")}" data-channel-link="{quote(category, safe="")}">{icon} {label}</a>' for category, icon, label in self.CHANNELS)
        mode = "離線範例" if report.mode == "demo" else report.health_label
        next_label = report.generated_at.replace(minute=17, second=0, microsecond=0)
        if next_label <= report.generated_at:
            next_label += timedelta(hours=1)
        empty = '<section class="empty">這一輪沒有可閱讀的繁中情報，系統不會用英文原文或範例資料冒充結果；下一次會自動再抓。</section>' if not clusters else ""
        return f'''<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#101722"><meta name="apple-mobile-web-app-capable" content="yes"><meta name="apple-mobile-web-app-title" content="今天紅什麼"><link rel="manifest" href="manifest.webmanifest"><link rel="icon" href="app-icon.svg"><link rel="apple-touch-icon" href="app-icon.svg"><title>今天紅什麼</title><style>
:root{{color-scheme:dark;--bg:#0a0e16;--panel:#121a28;--line:#2b3950;--text:#f5f4ef;--muted:#aab6c8;--cyan:#55d9ff;--pink:#ff6f9f;--gold:#ffc769}}*{{box-sizing:border-box}}html{{scroll-behavior:smooth}}body{{margin:0;background:radial-gradient(circle at 10% 0,#193450 0,transparent 34%),radial-gradient(circle at 100% 15%,#3a1e3e 0,transparent 30%),var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}main{{max-width:900px;margin:auto;padding:20px 14px 54px}}.shell{{border:1px solid var(--line);background:#0e1522e8;box-shadow:0 25px 80px #0008;border-radius:22px;overflow:hidden}}header,section{{padding:18px 22px;border-bottom:1px solid var(--line)}}.topline{{display:flex;justify-content:space-between;color:var(--muted);font-size:.85rem}}.status{{color:#75dfb4}}.status.degraded{{color:var(--gold)}}.updated{{font-size:.82rem;color:var(--muted);margin:7px 0 0}}.metrics{{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:14px}}.metrics div{{padding:10px;border:1px solid #334159;border-radius:12px;background:#ffffff08}}.metrics b{{display:block;font-size:1.2rem}}.metrics span,.muted,small{{color:var(--muted);font-size:.78rem}}.eyebrow{{color:var(--cyan);font-size:.82rem;font-weight:800;letter-spacing:.06em}}h1{{font-size:clamp(1.8rem,5vw,3rem);line-height:1.08;margin:9px 0}}h2{{font-size:1.05rem;margin:0}}h3{{margin:6px 0;font-size:1rem;line-height:1.4}}p{{color:#d5dbe6;line-height:1.55}}.hero{{display:grid;grid-template-columns:1.45fr .55fr;gap:18px;background:linear-gradient(130deg,#16263a,#231b31)}}.hero-mark{{display:grid;place-items:center;border-radius:16px;background:linear-gradient(145deg,#263c5d,#622d58);font-size:4rem;color:var(--gold)}}.decision,.source-pill{{display:inline-block;border:1px solid #5a7899;border-radius:999px;padding:4px 8px;font-size:.78rem;color:#eaf7ff;background:#ffffff0a}}.hero-actions,.compact-actions{{display:flex;gap:10px;align-items:center;flex-wrap:wrap}}.text-link{{color:var(--cyan);font-weight:800;text-decoration:none;font-size:.86rem}}.quick-nav{{display:flex;gap:8px;overflow:auto;padding:12px 22px;border-bottom:1px solid var(--line);white-space:nowrap}}.quick-nav a{{color:#dce8f6;border:1px solid #40516a;border-radius:999px;padding:7px 10px;text-decoration:none;font-size:.82rem}}.compact{{display:flex;justify-content:space-between;gap:12px;padding:12px 0;border-bottom:1px solid #263247}}.compact:last-child{{border-bottom:0}}.compact p{{margin:5px 0 0;font-size:.86rem}}button{{border:1px solid #40516a;border-radius:8px;background:#202c3d;color:#dce8f6;padding:5px 8px;cursor:pointer}}.ranking{{list-style:none;padding:0;margin:0}}.ranking li{{display:grid;grid-template-columns:22px 1fr auto;gap:9px;align-items:center;padding:10px 0;border-bottom:1px solid #263247}}.ranking b{{color:var(--gold)}}.visual-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px}}.image-card{{overflow:hidden;border:1px solid #334159;border-radius:14px;background:var(--panel)}}.image-card img{{display:block;width:100%;aspect-ratio:16/9;object-fit:cover;background:#263246}}.image-card div{{padding:12px}}.channel{{border-bottom:1px solid var(--line)}}summary{{cursor:pointer;display:flex;gap:8px;align-items:center;padding:17px 22px;list-style:none}}summary::-webkit-details-marker{{display:none}}summary::after{{content:'⌄';color:var(--muted);margin-left:4px}}details[open] summary::after{{content:'⌃'}}summary small{{margin-left:auto}}.channel-body{{padding:0 22px 14px}}.no-data{{margin:4px 0 12px;color:var(--muted);font-size:.9rem}}.trust{{color:var(--muted);font-size:.86rem}}.trust ul{{color:#ffb4c8}}.empty{{color:#ffd6df;background:#301c2a}}@media(max-width:650px){{main{{padding:0}}.shell{{border-radius:0;min-height:100vh}}header,section{{padding:17px}}.quick-nav{{padding:12px 17px}}.metrics{{grid-template-columns:repeat(3,1fr)}}.hero{{grid-template-columns:1fr}}.hero-mark{{min-height:105px}}.compact{{display:block}}.compact-actions{{margin-top:10px}}summary{{padding:16px 17px}}.channel-body{{padding:0 17px 12px}}}}</style></head><body><main><div class="shell"><header><div class="topline"><span>你的今日情報</span><span class="status{' degraded' if report.mode == 'live' and report.health_label != '來源正常' else ''}">● {escape(mode)}</span></div><p class="updated">更新：{escape(format_taiwan_time(report.generated_at))}　｜　預計下次：{escape(format_taiwan_time(next_label))}</p><div class="metrics"><div><b>{len(clusters)}</b><span>則可讀情報</span></div><div><b>{sum(1 for item in clusters if item.source_type_label in {'搜尋熱度','社群討論'})}</b><span>個流行訊號</span></div><div><b>{sum(1 for item in clusters if item.category == '股票與市場')}</b><span>則持股消息</span></div></div></header><nav class="quick-nav" aria-label="快速跳到分類">{shortcuts}</nav>{self._hero(hero) if hero else ''}{empty}{'<section><div class="eyebrow">今日另外兩件</div><h2>不用滑很多，先看這些就好</h2>'+pick_html+'</section>' if other_picks else ''}{'<section><div class="eyebrow">大家正在關注</div><h2>現在紅什麼</h2><ol class="ranking">'+trend_html+'</ol></section>' if trends else ''}{'<section class="visuals"><div class="eyebrow">影片精選</div><h2>有可信縮圖才顯示</h2><div class="visual-grid">'+visual_html+'</div></section>' if visuals else ''}<section><div class="eyebrow">你的關注頻道</div><h2>想看哪類，再點開就好</h2></section>{channels}<section class="trust"><b>情報判讀</b><p>官方公開資訊適合確認行程；媒體、搜尋與社群訊號適合掌握脈動；社群討論不等於事實。股票內容不是買賣建議。</p>{'<ul>'+warning_html+'</ul>' if warning_html else ''}</section></div></main><script>const key='daily-intelligence-item-feedback-v2';const state=JSON.parse(localStorage.getItem(key)||'{{"more":[],"less":[]}}');const save=()=>localStorage.setItem(key,JSON.stringify(state));const refresh=()=>{{document.querySelectorAll('[data-item]').forEach(card=>{{const id=card.dataset.item;card.style.display=state.less.includes(id)?'none':'';card.style.outline=state.more.includes(id)?'2px solid #55d9ff':'';}});document.querySelectorAll('.channel-body').forEach(body=>{{const cards=[...body.querySelectorAll('[data-item]')];cards.sort((a,b)=>Number(state.more.includes(b.dataset.item))-Number(state.more.includes(a.dataset.item))).forEach(card=>body.append(card));}});}};document.addEventListener('click',event=>{{const button=event.target.closest('[data-vote]');if(!button)return;const card=button.closest('[data-item]');const id=card.dataset.item;const list=button.dataset.vote==='more'?state.more:state.less;const other=button.dataset.vote==='more'?state.less:state.more;if(!list.includes(id))list.push(id);const found=other.indexOf(id);if(found>=0)other.splice(found,1);save();refresh();}});document.querySelectorAll('[data-channel-link]').forEach(link=>link.addEventListener('click',()=>{{const channel=document.getElementById(link.dataset.channelLink);if(channel)channel.open=true;}}));refresh();</script></body></html>'''
