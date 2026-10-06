/* Browser-local article bookmarks and named topic preferences. No tokens/API. */
(() => {
  "use strict";
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
  function renderSettings() {
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
      if (!article || typeof article.url !== "string" || !/^https?:\/\//.test(article.url)) continue;
      const row = document.createElement("p");
      const link = document.createElement("a");
      link.className = "text-link";
      link.href = article.url;
      link.textContent = article.title;
      const remove = document.createElement("button");
      remove.dataset.removeSaved = id;
      remove.textContent = "取消收藏";
      row.append(link, " ", remove);
      saved.append(row);
    }
    if (!saved.children.length) saved.textContent = "收藏後，可以在這裡找回原文。";
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
        if (action === "save") button.textContent = active ? "已收藏 · 取消" : "收藏這篇";
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
          const link = card.querySelector("a.text-link");
          state.saved[id] = {title: card.querySelector("h1,h3").textContent, url: link.href};
          announce("只收藏這篇；可在「收藏與偏好」找回。");
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
  refresh();
  if (!persistent) announce("目前使用暫存偏好。");
  // The timestamp indicates the completed check, not a guaranteed next run.
  const checked = document.querySelector("[data-checked]");
  const age = (Date.now() - Date.parse(checked.dataset.checked)) / 60000;
  if (age > 90) document.getElementById("freshness-note").textContent = "這份報告已超過 90 分鐘，排程可能延遲；請檢查最新頁面或手動產生報告。";
})();
