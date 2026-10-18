/* Browser-local article bookmarks and named topic preferences. No tokens/API. */
(() => {
  "use strict";
  // A lightweight Korean-editorial visual refresh, injected after the base
  // styles so the report remains a single, portable HTML file.
  const style = document.createElement("style");
  style.textContent = `
    :root{color-scheme:light;--bg:#f6f3f2;--panel:#fffdfc;--line:#ece5e5;--text:#292733;--muted:#817c88;--cyan:#8c72d8;--pink:#e88caa;--gold:#c58b47}
    body{background:radial-gradient(circle at 8% 0,#eee7fb 0,transparent 34%),radial-gradient(circle at 100% 12%,#f9e7ec 0,transparent 30%),var(--bg);color:var(--text)}
    .shell{border-color:#eee8eb;background:#fffdfcf2;box-shadow:0 20px 55px #6a526510}
    header{background:linear-gradient(135deg,#f2edfb,#fff0f3);border-color:#ebe4f1}
    .topline,.updated,.muted,small{color:var(--muted)}
    .status{color:#4e9c7e}.status.degraded{color:#ad7937}
    h1,h2,h3,b{color:#292733}p{color:#55515d}
    .eyebrow,.text-link{color:#765bc6}.decision,.source-pill{border-color:#ded3f2;color:#5e4c89;background:#f8f4ff}
    .quick-nav a{color:#514b5a;border-color:#e8e0e8;background:#fff;border-radius:999px;box-shadow:0 2px 8px #46354a0a}
    .channel{border-color:#eee8eb}.channel[open]{background:#fff}
    .compact{border-color:#f0ebef}.image-card{border-color:#eee8eb;background:#fff;box-shadow:0 5px 18px #4b3a4a0a}
    button{border-color:#e7dfee;background:#f7f3fb;color:#51466c;border-radius:999px;padding:8px 12px;font-weight:650}
    button[aria-pressed=true]{border-color:#ad99df;background:#efe9fb;color:#59439d}
    .hero{background:linear-gradient(135deg,#f4effb,#fff1f4)}
    .alerts{border-left-color:#e58aa0}.saved{border-left-color:#c58b47}
    #feedback-notice{color:#765bc6}.trust{font-size:.78rem}
    .brief-summary{margin:7px 0 4px;font-size:.92rem;line-height:1.45}
    .more-actions{display:inline-block;position:relative}
    .more-actions>summary{display:inline-block;padding:8px 10px;border:1px solid #eee8f0;border-radius:999px;color:#817c88;font-size:.8rem;list-style:none}
    .more-actions>summary::-webkit-details-marker{display:none}
    .more-actions>div{display:flex;gap:6px;flex-wrap:wrap;margin-top:6px}
    .more-actions button{font-size:.78rem}
    .updated>details{display:inline-block;margin-left:6px}
    .updated>details summary{display:inline-block;padding:3px 7px;border-radius:999px;background:#fff;color:#786d8c;font-size:.72rem}
    @media(max-width:650px){main{padding:0}.shell{border:0}.quick-nav{gap:7px}.quick-nav a{padding:8px 11px}.compact-actions{gap:7px}.compact-actions button{min-height:38px}}
  `;
  document.head.append(style);
  const key = "daily-intelligence-preferences-v3";
  const emptyState = () => ({saved: {}, hidden: [], topics: {}});
  let state = emptyState();
  let persistent = true;
  try {
    const stored = JSON.parse(localStorage.getItem(key) || "null");
    if (stored && typeof stored.saved === "object" && stored.saved !== null &&
        !Array.isArray(stored.saved) && Array.isArray(stored.hidden) &&
        stored.topics && typeof stored.topics === "object" && !Array.isArray(stored.topics)) state = stored;
  } catch (_) { persistent = false; }
  const notice = document.getElementById("feedback-notice");
  function announce(message) {
    notice.textContent = message + (persistent ? "" : "（瀏覽器無法儲存，目前只保留到本次關閉頁面。）");
  }
  function save() {
    try { localStorage.setItem(key, JSON.stringify(state)); }
    catch (_) { persistent = false; }
  }
  function score(card) { return Number(state.topics[card.dataset.topic] || 0); }
  function isWatchlist(category) {
    return ["新番與串流新劇", "新番動漫", "Netflix 新劇", "Disney+ 新劇"].includes(category);
  }
  function renderSettings() {
    const watchSummary = document.querySelector("#preferences summary b");
    if (watchSummary) watchSummary.textContent = "我的收藏／想看清單";
    const savedHeading = document.querySelector("#saved-articles").previousElementSibling;
    if (savedHeading) savedHeading.textContent = "想看的作品與收藏文章";
    const visualHeading = document.querySelector(".visuals h2");
    if (visualHeading) visualHeading.textContent = "先看圖片，再決定要不要點開";
    const visualLabel = document.querySelector(".visuals .eyebrow");
    if (visualLabel) visualLabel.textContent = "圖片速覽";
    const trustNote = document.querySelector(".trust p");
    if (trustNote) trustNote.textContent = "社群熱度不等於事實；新劇上架日以官方公告為準。股票內容不是買賣建議。";
    const topics = document.getElementById("topic-preferences");
    topics.replaceChildren();
    for (const [topic, value] of Object.entries(state.topics)) {
      if (value !== 1 && value !== -1) continue;
      const button = document.createElement("button");
      button.dataset.removeTopic = topic;
      button.textContent = `${topic}：${value === 1 ? "多看" : "少看"} · 取消`;
      topics.append(button);
    }
    if (!topics.children.length) topics.textContent = "尚未設定主題偏好。";
    const saved = document.getElementById("saved-articles");
    saved.replaceChildren();
    for (const [id, article] of Object.entries(state.saved)) {
      if (!article || typeof article.title !== "string") continue;
      const row = document.createElement("p");
      if (typeof article.url === "string" && /^https?:\/\//.test(article.url)) {
        const link = document.createElement("a");
        link.className = "text-link";
        link.href = article.url;
        link.textContent = article.title;
        row.append(link);
      } else {
        const title = document.createElement("b");
        title.textContent = article.title;
        row.append(title);
      }
      if (article.summary) {
        const summary = document.createElement("small");
        summary.style.display = "block";
        summary.textContent = article.summary;
        row.append(summary);
      }
      row.append(" ");
      const remove = document.createElement("button");
      remove.dataset.removeSaved = id;
      remove.textContent = "取消收藏";
      row.append(link, " ", remove);
      saved.append(row);
    }
    if (!saved.children.length) saved.textContent = "目前還沒有收藏。想追的作品或喜歡的小提醒，都可以收在這裡。";
    const count = Object.keys(state.saved).length;
    const summary = document.querySelector("#preferences summary");
    let countLabel = summary.querySelector(".saved-count");
    if (!countLabel) { countLabel = document.createElement("small"); countLabel.className = "saved-count"; summary.append(countLabel); }
    countLabel.textContent = `${count} 部／篇`;
    document.getElementById("restore-hidden").textContent = `恢復隱藏的文章（${state.hidden.length}）`;
  }
  function refresh() {
    document.querySelectorAll("[data-item]").forEach(card => {
      const id = card.dataset.item;
      card.hidden = state.hidden.includes(id);
      card.classList.toggle("saved", Object.hasOwn(state.saved, id));
      card.querySelectorAll("[data-action]").forEach(button => {
        const action = button.dataset.action;
        const active = action === "save" ? Object.hasOwn(state.saved, id) :
          action === "like" ? state.topics[card.dataset.topic] === 1 :
          action === "dislike" ? state.topics[card.dataset.topic] === -1 : false;
        button.setAttribute("aria-pressed", String(active));
        if (action === "save") button.textContent = active ?
          isWatchlist(card.dataset.category) ? "已加入清單 · 取消" : "已收藏 · 取消" :
          isWatchlist(card.dataset.category) ? "加入想看清單" : card.dataset.category === "每日充電" ? "收藏這個提醒" : "收藏這篇";
      });
    });
    document.querySelectorAll(".channel-body").forEach(body => {
      const cards = [...body.querySelectorAll("[data-item]")];
      cards.forEach((card, index) => { if (!card.dataset.originalOrder) card.dataset.originalOrder = String(index + 1); });
      cards.sort((a, b) => score(b) - score(a) || Number(a.dataset.originalOrder) - Number(b.dataset.originalOrder))
        .forEach(card => body.append(card));
      const count = cards.filter(card => !card.hidden).length;
      if (cards.length) body.closest("details").querySelector("summary small").textContent = `${count}／3 則${count < cards.length ? " · 有隱藏" : ""}`;
    });
    renderSettings();
  }
  document.addEventListener("click", event => {
    const button = event.target.closest("button");
    if (!button) return;
    if (button.dataset.removeTopic) {
      delete state.topics[button.dataset.removeTopic]; announce("已取消這個主題的偏好。");
    } else if (button.dataset.removeSaved) {
      delete state.saved[button.dataset.removeSaved]; announce("已取消收藏。");
    } else if (button.id === "restore-hidden") {
      state.hidden = []; announce("已恢復隱藏的文章。");
    } else if (button.id === "reset-topics") {
      state.topics = {}; announce("已清除主題偏好，收藏不受影響。");
    } else if (button.dataset.action) {
      const card = button.closest("[data-item]");
      const id = card.dataset.item;
      const topic = card.dataset.topic;
      if (button.dataset.action === "save") {
        if (Object.hasOwn(state.saved, id)) { delete state.saved[id]; announce("已取消收藏這篇。"); }
        else {
          const link = card.querySelector("a.text-link[href^='http']");
          const summary = card.querySelector(".boost-action")?.innerText || card.querySelector(".brief-summary")?.innerText || "";
          state.saved[id] = {title: card.querySelector("h1,h3").textContent, summary, url: link?.href || "", category: card.dataset.category};
          announce(isWatchlist(card.dataset.category) ? "已加入想看清單；點上方「我的想看清單」就能找到。" : card.dataset.category === "每日充電" ? "已收藏這個提醒；點上方「我的想看清單」就能回看。" : "已收藏；點上方「我的想看清單」就能找回。");
        }
      } else if (button.dataset.action === "hide") {
        if (!state.hidden.includes(id)) state.hidden.push(id);
        announce("只隱藏這篇，可在「收藏與偏好」恢復。");
      } else if (topic) {
        const value = button.dataset.action === "like" ? 1 : -1;
        if (state.topics[topic] === value) delete state.topics[topic];
        else state.topics[topic] = value;
        announce(`已調整「${topic}」的順序偏好；不會替其他文章加框，也不會增加來源抓取數。`);
      }
    } else return;
    save(); refresh();
  });
  document.querySelectorAll("[data-channel-link]").forEach(link => link.addEventListener("click", () => {
    const channel = document.getElementById(link.dataset.channelLink);
    if (channel) channel.open = true;
  }));
  document.querySelectorAll("[data-watchlist-link]").forEach(link => link.addEventListener("click", () => {
    const watchlist = document.getElementById("preferences");
    if (watchlist) watchlist.open = true;
  }));
  refresh();
  if (!persistent) announce("目前使用暫存偏好。");
  // The timestamp indicates the completed check, not a guaranteed next run.
  const checked = document.querySelector("[data-checked]");
  const updated = document.querySelector(".updated");
  const statusLines = updated.innerText.split("\n").map(line => line.trim()).filter(Boolean);
  if (statusLines.length > 1) {
    updated.textContent = statusLines[0];
    const extra = document.createElement("details");
    const summary = document.createElement("summary");
    summary.textContent = "更新細節";
    const detail = document.createElement("small");
    detail.style.display = "block";
    detail.textContent = statusLines.slice(1).join(" · ");
    extra.append(summary, detail);
    updated.append(" ", extra);
  }
  document.getElementById("freshness-note").textContent = "先看精選 → 點有興趣的分類 → 想追就加入清單。";
  const age = (Date.now() - Date.parse(checked.dataset.checked)) / 60000;
  if (age > 90) document.getElementById("freshness-note").textContent = "這份報告已超過 90 分鐘，排程可能延遲；請檢查最新頁面或手動產生報告。";
})();
