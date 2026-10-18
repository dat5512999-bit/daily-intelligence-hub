/* Real headless browser acceptance tests; no production dependencies. */
const assert = require("node:assert/strict");
const {pathToFileURL} = require("node:url");
const path = require("node:path");
const {chromium} = require("playwright");

(async () => {
  const browser = await chromium.launch({channel: "chrome", headless: true});
  try {
    const context = await browser.newContext({viewport: {width: 390, height: 844}});
    const page = await context.newPage();
    const errors = [];
    page.on("pageerror", error => errors.push(error.message));
    const url = pathToFileURL(path.resolve(process.env.TEST_REPORT || "reports/preview.html")).href;
    await page.goto(url);
    await page.evaluate(() => localStorage.clear());
    await page.reload();
    const game = page.locator("details.channel").filter({has: page.locator("summary b", {hasText: "遊戲與電競"})});
    await game.locator(":scope > summary").click();
    const rows = game.locator("article");
    assert.equal(await rows.count(), 3);
    const row = rows.first();
    const id = await row.getAttribute("data-item");
    await row.getByRole("button", {name: "收藏這篇", exact: true}).click();
    assert.equal(await game.locator("article.saved").count(), 1, "Only the selected article is bookmarked");
    await page.locator("[data-watchlist-link]").click();
    assert.equal(await page.locator("#preferences").evaluate(node => node.open), true, "The visible quick link opens the saved-items list");
    assert.match(await page.locator("#preferences summary").textContent(), /我的收藏／想看清單/);
    const boost = page.locator("details.channel").filter({has: page.locator("summary b", {hasText: "每日充電"})});
    await boost.locator(":scope > summary").click();
    const boostCard = boost.locator("article").first();
    const boostTitle = await boostCard.locator("h3").textContent();
    await boostCard.getByRole("button", {name: "收藏這個提醒", exact: true}).click();
    assert.equal(await page.locator("#saved-articles").getByText(boostTitle, {exact: true}).count(), 1, "The saved reflection remains readable without a fake external link");
    assert.match(await page.locator("#saved-articles").innerText(), /今天試試/);
    await page.reload();
    assert.equal(await page.locator(`article[data-item="${id}"].saved`).count(), 1);
    await game.locator(":scope > summary").click();
    await page.locator(`article[data-item="${id}"]`).getByRole("button", {name: "已收藏 · 取消", exact: true}).click();
    assert.equal(await game.locator("article.saved").count(), 0);
    const pref = game.locator('[data-action="like"]').last();
    const topic = await pref.locator("xpath=ancestor::article[1]").getAttribute("data-topic");
    await pref.locator("xpath=ancestor::details[1]").locator("summary").click();
    await pref.click();
    assert.equal(await rows.first().getAttribute("data-topic"), topic, "Preferred named topic is ordered first");
    assert.equal(await game.locator("article.saved").count(), 0, "Topic preference does not add bookmark borders");
    await page.reload();
    await game.locator(":scope > summary").click();
    assert.equal(await rows.first().getAttribute("data-topic"), topic, "Topic preference survives the next page load");
    await rows.first().locator("details.more-actions summary").click();
    await rows.first().getByRole("button", {name: "隱藏這篇", exact: true}).click();
    assert.equal(await game.locator("article:visible").count(), 2);
    await page.locator("#preferences summary").click();
    await page.locator("#restore-hidden").click();
    assert.equal(await game.locator("article:visible").count(), 3);
    await page.locator("#reset-topics").click();
    assert.equal(await rows.first().getAttribute("data-item"), id, "Clearing preferences restores source ordering");
    await page.evaluate(() => {
      const card = document.createElement("article");
      card.dataset.item = "release-test";
      card.dataset.category = "新番與串流新劇";
      card.innerHTML = '<h3>片單測試新番</h3><a class="text-link" href="https://example.com/release-test">看原文</a><button data-action="save">加入想看清單</button>';
      document.body.append(card);
    });
    const release = page.locator('article[data-item="release-test"]');
    await release.getByRole("button", {name: "加入想看清單"}).click();
    assert.equal(await page.locator('#saved-articles a').filter({hasText: "片單測試新番"}).count(), 1);
    assert.equal(await release.locator('[data-action="save"]').textContent(), "已加入清單 · 取消");
    await page.locator("[data-watchlist-link]").click();
    assert.equal(await page.locator("#preferences").evaluate(node => node.open), true);
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true, "No mobile overflow");
    const artifactDir = process.env.TEST_ARTIFACT_DIR || "reports";
    await page.screenshot({path: path.join(artifactDir, "qa-mobile.png"), fullPage: true});
    assert.deepEqual(errors, []);
    await context.close();

    const blocked = await browser.newContext({viewport: {width: 390, height: 844}});
    await blocked.addInitScript(() => {
      Object.defineProperty(window, "localStorage", {get() { throw new Error("blocked"); }});
    });
    const blockedPage = await blocked.newPage();
    await blockedPage.goto(url);
    assert.match(await blockedPage.locator("#feedback-notice").textContent(), /暫存/);
    await blockedPage.locator('.hero [data-action="save"]').click();
    assert.match(await blockedPage.locator("#feedback-notice").textContent(), /無法儲存/);
    await blocked.close();
    console.log("PASS: individual bookmarks, named topics, reload persistence, undo, mobile layout, storage fallback");
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
