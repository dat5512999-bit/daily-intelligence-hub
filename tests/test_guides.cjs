/* Mobile acceptance and visual evidence for the two new channels. */
const assert = require('node:assert/strict');
const {pathToFileURL} = require('node:url');
const path = require('node:path');
const {chromium} = require('playwright');

(async () => {
  const browser = await chromium.launch({channel: 'chrome', headless: true});
  try {
    const page = await browser.newPage({viewport: {width: 390, height: 844}});
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.goto(pathToFileURL(path.resolve(process.argv[2] || 'reports/preview.html')).href);
    const github = page.locator('details.channel#GitHub');
    await github.locator(':scope > summary').click();
    assert.equal(await github.locator('article').count(), 3);
    const first = github.locator('article').first();
    assert.match(await first.textContent(), /用在哪裡：[\s\S]*使用例子：[\s\S]*上手門檻：/);
    assert.equal(await github.locator('img').count(), 0, 'No fake screenshots or blank image placeholders');
    await first.screenshot({path: 'reports/qa-github-guide.png'});
    const knowledge = page.locator('details.channel').filter({has: page.locator('summary b', {hasText: '冷知識 · 每天三則'})});
    await knowledge.locator(':scope > summary').click();
    assert.equal(await knowledge.locator('article').count(), 3);
    assert.match(await knowledge.textContent(), /非即時新聞/);
    await knowledge.screenshot({path: 'reports/qa-knowledge.png'});
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
    assert.deepEqual(errors, []);
    console.log('PASS: three GitHub guides, three attributed facts, mobile layout, no fake images');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
