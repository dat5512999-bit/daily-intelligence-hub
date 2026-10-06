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
    const url = pathToFileURL(path.resolve("reports/preview.html")).href;
    await page.goto(url);
    await page.evaluate(() => localStorage.clear());
    await page.reload();
    const game = page.locator("details.channel").filter({has: page.locator("summary b", {hasText: "遊戲與電競"})});
    await game.locator("summary").click();
    const rows = game.locator("article");
    assert.equal(await rows.count(), 3);
    const row = rows.first();
    const id = await row.getAttribute("data-item");
    await row.getByRole("button", {name: "收藏這篇", exact: true}).click();
    assert.equal(await game.locator("article.saved").count(), 1, "Only the selected article is bookmarked");
    await page.reload();
    assert.equal(await page.locator(`article[data-item="${id}"].saved`).count(), 1);
    await game.locator("summary").click();
    await page.locator(`article[data-item="${id}"]`).getByRole("button", {name: "已收藏 · 取消", exact: true}).click();
    assert.equal(await game.locator("article.saved").count(), 0);
    const pref = game.locator('[data-action="like"]').last();
    const topic = await pref.locator("..").locator("..").getAttribute("data-topic");
    await pref.click();
    assert.equal(await rows.first().getAttribute("data-topic"), topic, "Preferred named topic is ordered first");
    assert.equal(await game.locator("article.saved").count(), 0, "Topic preference does not add bookmark borders");
    await page.reload();
    await game.locator("summary").click();
    assert.equal(await rows.first().getAttribute("data-topic"), topic, "Topic preference survives the next page load");
    await rows.first().getByRole("button", {name: "隱藏這篇", exact: true}).click();
    assert.equal(await game.locator("article:visible").count(), 2);
    await page.locator("#preferences summary").click();
    await page.locator("#restore-hidden").click();
    assert.equal(await game.locator("article:visible").count(), 3);
    await page.locator("#reset-topics").click();
    assert.equal(await rows.first().getAttribute("data-item"), id, "Clearing preferences restores source ordering");
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true, "No mobile overflow");
    await page.screenshot({path: "reports/qa-mobile.png", fullPage: true});
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
