"""Mixed-component, mobile-first dashboard renderer."""

from __future__ import annotations

from html import escape
from urllib.parse import quote

from app.domain.models import DailyReport, IntelligenceCluster
from app.output.time_format import format_taiwan_time


class HtmlPreviewRenderer:
    """Render a personal intelligence dashboard, not a uniform news-card feed."""

    @staticmethod
    def _translate(url: str) -> str:
        return f"https://translate.google.com/translate?sl=auto&tl=zh-TW&u={quote(url, safe='')}"

    @staticmethod
    def _link(cluster: IntelligenceCluster, label: str = "看原文") -> str:
        return f'<a class="text-link" href="{escape(cluster.primary_url, quote=True)}">{label} ↗</a>'

    @staticmethod
    def _item_id(cluster: IntelligenceCluster, index: int, area: str) -> str:
        return escape(f"{area}:{index}:{cluster.primary_url}", quote=True)

    def _compact_row(self, cluster: IntelligenceCluster, index: int, area: str = "list") -> str:
        item_id = self._item_id(cluster, index, area)
        return (
            f'<article class="compact" data-item="{item_id}"><div class="compact-main">'
            f'<span class="source-pill">{escape(cluster.source_type_label)}</span><h3>{escape(cluster.title)}</h3>'
            f'<p>{escape(cluster.decision_label)} · {escape(cluster.summary)}</p></div>'
            f'<div class="compact-actions">{self._link(cluster)}<button data-vote="more">多看這則</button><button data-vote="less">少看這則</button></div></article>'
        )

    def _image_card(self, cluster: IntelligenceCluster, index: int) -> str:
        item_id = self._item_id(cluster, index, "visual")
        image = escape(cluster.image_url, quote=True)
        return (
            f'<article class="image-card" data-item="{item_id}"><img loading="lazy" src="{image}" alt="">'
            f'<div><span class="source-pill">{escape(cluster.source_type_label)}</span><h3>{escape(cluster.title)}</h3>'
            f'<p>{escape(cluster.decision_label)}</p>{self._link(cluster)}</div></article>'
        )

    def _hero(self, cluster: IntelligenceCluster) -> str:
        visual = f'<img src="{escape(cluster.image_url, quote=True)}" alt="">' if cluster.image_url else '<div class="hero-orb">✦</div>'
        return (
            f'<section class="hero"><div class="hero-copy"><span>今日最值得花時間</span><h1>{escape(cluster.title)}</h1>'
            f'<p class="decision">{escape(cluster.decision_label)}</p><p>{escape(cluster.summary)}</p>'
            f'<div class="hero-actions">{self._link(cluster, "進入情報")}<a class="text-link muted" href="{escape(self._translate(cluster.primary_url), quote=True)}">繁中翻譯</a></div></div>{visual}</section>'
        )

    def render(self, report: DailyReport) -> str:
        clusters = list(report.clusters)
        ai_hero = next((item for item in clusters if item.category == "AI／Codex"), None)
        hero = ai_hero or (clusters[0] if clusters else None)
        remaining = [item for item in clusters if item is not hero]
        alerts = [item for item in remaining if item.decision_label.startswith("現在看") and "持股" not in item.decision_label][:3]
        remaining = [item for item in remaining if item not in alerts]
        visuals = [item for item in remaining if item.image_url][:4]
        remaining = [item for item in remaining if item not in visuals]
        rankings = [item for item in remaining if item.source_type_label in {"搜尋熱度", "社群討論"}][:5]
        remaining = [item for item in remaining if item not in rankings]
        stocks = [item for item in remaining if item.category == "股票與市場"][:3]
        events = [item for item in remaining if item.category in {"生活流行", "台中好康與活動"}][:4]
        updates = [item for item in remaining if item.category in {"AI／Codex", "GitHub", "遊戲與電競", "動漫與娛樂"}][:6]
        mode = "離線範例" if report.mode == "demo" else report.health_label
        warning_html = "".join(f"<li>{escape(error)}</li>" for error in report.source_errors)
        alert_html = "".join(f'<div class="alert">⚠ <b>{escape(item.title)}</b><span>{escape(item.decision_label)}</span>{self._link(item)}</div>' for item in alerts)
        ranking_html = "".join(f'<li><b>{index}</b><span>{escape(item.title)}</span><small>{escape(item.source_type_label)}</small>{self._link(item)}</li>' for index, item in enumerate(rankings, 1))
        visual_html = "".join(self._image_card(item, index) for index, item in enumerate(visuals, 1))
        stock_html = "".join(self._compact_row(item, index, "stock") for index, item in enumerate(stocks, 1))
        update_html = "".join(self._compact_row(item, index, "update") for index, item in enumerate(updates, 1))
        event_html = "".join(f'<li><span>●</span><div><b>{escape(item.title)}</b><p>{escape(item.decision_label)}</p>{self._link(item)}</div></li>' for item in events)
        empty = '<section class="empty">本次資料不足，系統不會使用範例內容冒充即時情報。</section>' if not clusters else ""
        return f'''<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#101722"><meta name="apple-mobile-web-app-capable" content="yes"><meta name="apple-mobile-web-app-title" content="今天紅什麼"><link rel="manifest" href="manifest.webmanifest"><link rel="icon" href="app-icon.svg"><link rel="apple-touch-icon" href="app-icon.svg"><title>今天紅什麼</title><style>
:root{{color-scheme:dark;--bg:#0a0e16;--panel:#121a28;--line:#2b3950;--text:#f5f4ef;--muted:#aab6c8;--cyan:#55d9ff;--pink:#ff6f9f;--gold:#ffc769}}*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(circle at 10% 0,#193450 0,transparent 34%),radial-gradient(circle at 100% 15%,#3a1e3e 0,transparent 30%),var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}main{{max-width:980px;margin:auto;padding:20px 14px 54px}}.shell{{border:1px solid var(--line);background:#0e1522e8;box-shadow:0 25px 80px #0008;border-radius:22px;overflow:hidden}}header{{padding:20px 22px;border-bottom:1px solid var(--line)}}.topline{{display:flex;justify-content:space-between;color:var(--muted);font-size:.82rem}}.status{{color:#75dfb4}}.status.degraded{{color:var(--gold)}}.metrics{{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:16px}}.metrics div{{padding:11px;border:1px solid #334159;border-radius:12px;background:#ffffff08}}.metrics b{{display:block;font-size:1.25rem}}.metrics span{{color:var(--muted);font-size:.78rem}}section{{padding:18px 22px;border-bottom:1px solid var(--line)}}.hero{{display:grid;grid-template-columns:1.4fr .6fr;gap:18px;background:linear-gradient(130deg,#16263a,#231b31)}}.hero span,.eyebrow{{color:var(--cyan);font-size:.82rem;font-weight:800;letter-spacing:.08em}}h1{{font-size:clamp(1.8rem,5vw,3rem);line-height:1.08;margin:9px 0}}h2{{font-size:1.05rem;margin:0 0 12px}}h3{{margin:6px 0;font-size:1rem;line-height:1.4}}p{{color:#d5dbe6;line-height:1.55}}.decision,.source-pill{{display:inline-block;border:1px solid #5a7899;border-radius:999px;padding:4px 8px;font-size:.78rem;color:#eaf7ff;background:#ffffff0a}}.hero img,.hero-orb{{width:100%;aspect-ratio:1;object-fit:cover;border-radius:16px;background:linear-gradient(145deg,#263c5d,#622d58);display:grid;place-items:center;font-size:4rem;color:var(--gold)}}.hero-actions,.compact-actions{{display:flex;gap:10px;align-items:center;flex-wrap:wrap}}.text-link{{color:var(--cyan);font-weight:800;text-decoration:none;font-size:.86rem}}.muted{{color:var(--muted)}}.alert-stack{{display:grid;gap:8px}}.alert{{display:flex;gap:9px;align-items:center;flex-wrap:wrap;padding:11px;border-left:3px solid var(--pink);background:#301c2a;border-radius:8px}}.alert span{{color:#ffd6e3;font-size:.82rem}}.ranking{{list-style:none;padding:0;margin:0}}.ranking li{{display:grid;grid-template-columns:28px 1fr auto auto;gap:9px;align-items:center;padding:11px 0;border-bottom:1px solid #263247}}.ranking b{{color:var(--gold)}}.ranking small{{color:var(--muted)}}.visual-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px}}.image-card{{overflow:hidden;border:1px solid #334159;border-radius:14px;background:var(--panel)}}.image-card img{{display:block;width:100%;aspect-ratio:16/9;object-fit:cover;background:#263246}}.image-card div{{padding:12px}}.image-card p{{font-size:.84rem;margin:8px 0}}.split{{display:grid;grid-template-columns:1fr 1fr;gap:0}}.split>section{{border-bottom:0}}.split>section+section{{border-left:1px solid var(--line)}}.compact{{display:flex;justify-content:space-between;gap:12px;padding:12px 0;border-bottom:1px solid #263247}}.compact p{{margin:5px 0 0;font-size:.86rem}}button{{border:1px solid #40516a;border-radius:8px;background:#202c3d;color:#dce8f6;padding:5px 8px;cursor:pointer}}.timeline{{list-style:none;padding:0;margin:0}}.timeline li{{display:flex;gap:12px;padding:8px 0;border-left:1px solid #465878;margin-left:6px;padding-left:14px}}.timeline li>span{{color:var(--pink);margin-left:-22px;background:#0e1522;padding:0 5px}}.timeline p{{margin:4px 0;font-size:.86rem}}.trust{{color:var(--muted);font-size:.86rem}}.trust ul{{color:#ffb4c8}}.empty{{color:#ffd6df;background:#301c2a}}@media(max-width:650px){{main{{padding:0}}.shell{{border-radius:0;min-height:100vh}}header,section{{padding:17px}}.metrics{{grid-template-columns:repeat(2,1fr)}}.hero,.split{{grid-template-columns:1fr}}.hero img,.hero-orb{{max-height:230px;aspect-ratio:16/8}}.split>section+section{{border-left:0;border-top:1px solid var(--line)}}.ranking li{{grid-template-columns:22px 1fr auto}}.ranking small{{display:none}}}}</style></head><body><main><div class="shell"><header><div class="topline"><span>個人 Daily Intelligence</span><span class="status{' degraded' if report.mode == 'live' and report.health_label != '來源正常' else ''}">● {mode}</span></div><p>{escape(format_taiwan_time(report.generated_at))} · {escape(report.health_note)}</p><div class="metrics"><div><b>{len(clusters)}</b><span>則情報</span></div><div><b>{sum(1 for item in clusters if item.source_type_label in {'搜尋熱度','社群討論'})}</b><span>個趨勢訊號</span></div><div><b>{sum(1 for item in clusters if item.category == '股票與市場')}</b><span>則持股雷達</span></div><div><b>{report.source_count}</b><span>個有效來源</span></div></div></header>{self._hero(hero) if hero else ''}{empty}{'<section><div class="eyebrow">ALERT</div><h2>現在要注意</h2><div class="alert-stack">'+alert_html+'</div></section>' if alerts else ''}{'<section><div class="eyebrow">RANKING</div><h2>現在大家在紅什麼</h2><ol class="ranking">'+ranking_html+'</ol></section>' if rankings else ''}{'<section><div class="eyebrow">VISUAL PICKS</div><h2>有圖才值得用圖</h2><div class="visual-grid">'+visual_html+'</div></section>' if visuals else ''}<div class="split">{'<section><div class="eyebrow">MARKET</div><h2>你的持股雷達</h2>'+stock_html+'</section>' if stocks else ''}{'<section><div class="eyebrow">UPDATES</div><h2>AI、GitHub、遊戲與動漫更新</h2>'+update_html+'</section>' if updates else ''}</div>{'<section><div class="eyebrow">TODAY</div><h2>今天可去／可安排</h2><ol class="timeline">'+event_html+'</ol></section>' if events else ''}<section class="trust"><b>情報判讀</b><p>官方公開資訊適合確認行程；媒體報導與搜尋熱度適合掌握脈動；社群討論不等於事實。股票內容不是買賣建議。</p>{'<ul>'+warning_html+'</ul>' if warning_html else ''}</section></div></main><script>const key='daily-intelligence-item-feedback-v1';const state=JSON.parse(localStorage.getItem(key)||'{{"more":[],"less":[]}}');const refresh=()=>document.querySelectorAll('[data-item]').forEach(card=>{{const id=card.dataset.item;card.style.display=state.less.includes(id)?'none':'';card.style.outline=state.more.includes(id)?'2px solid #55d9ff':'';}});document.addEventListener('click',event=>{{const button=event.target.closest('[data-vote]');if(!button)return;const card=button.closest('[data-item]');const id=card.dataset.item;const list=button.dataset.vote==='more'?state.more:state.less;const other=button.dataset.vote==='more'?state.less:state.more;if(!list.includes(id))list.push(id);const found=other.indexOf(id);if(found>=0)other.splice(found,1);localStorage.setItem(key,JSON.stringify(state));refresh();}});refresh();</script></body></html>'''
