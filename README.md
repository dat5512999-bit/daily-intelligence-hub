# AI Daily Intelligence Research Hub

## 手機自動查看（GitHub Pages）

專案上傳到 GitHub 並啟用 Pages 後，GitHub 會在每天台灣時間約早上 8 點自動產生最新報告。手機只要開啟你的 Pages 網址，就能看到最新內容，也可以加入手機桌面當作 App 使用。

完整步驟請看 [GitHub Pages 手機使用說明](docs/GITHUB_PAGES_手機使用說明.md)。

每天從 GitHub Trending、Reddit、Hacker News、Google News RSS、Dcard、Google 熱門搜尋與 TikTok 公開趨勢收集公開訊號，整理為可在 3–5 分鐘讀完的 Markdown 與 HTML Daily Intelligence Report。

目前定位為「今天紅什麼情報雷達」：新聞用來保底，Dcard 熱門、Google 熱門搜尋、TikTok 與 Reddit 圈內討論用來找出可能要滑社群才會知道的冷門苗頭；報告會清楚標示它們不是已查證新聞。頁面採效率情報雜誌設計，上方會顯示情報數、苗頭數、持股數與來源數。

預設個人化主題為 AI／Codex、遊戲與電競、動漫、台中即時事件、台中活動與股票市場。股票關注包含聯電、臻鼎、0050、精材、群創、星宇航空與機器人概念股。排行榜會保留分類平衡，避免整份報告只剩股市或地方新聞。這些主題可在 `config/interests.json` 調整，不需要帳號或 API Key。

目前版本：`0.9.4`。每次 Sprint 完成會同步更新 `VERSION` 與 `CHANGELOG.md`；Git commit 可作為可回復版本點。

## 快速開始

需要 Python 3.9+，且僅使用 Python 標準函式庫。

```bash
python main.py --demo
python main.py --live
python -m unittest discover -s tests -v
```

Windows 可直接雙擊 `start.bat`；它會自動使用系統 Python 或本機 Codex 已附帶的 Python，抓取即時資料後自動開啟預覽。若只想看範例，可雙擊 `start_demo.bat`。macOS/Linux 可執行 `sh start.sh`。輸出在 `reports/Daily_Report.md` 與 `reports/preview.html`。

## Sprint 1 範圍

- Demo Mode：離線內建資料。
- Live Mode：GitHub、Reddit、Hacker News、繁中 Google News 與使用者選定的 YouTube 頻道；單一來源失敗時仍輸出報告。
- 可解釋的跨來源排名、Markdown 報告、可雙擊開啟的 HTML 預覽。

## YouTube 頻道

在 `config/youtube_channels.json` 填入想追蹤頻道的 `channel_id` 與分類。系統只讀取這些公開頻道最近上傳的影片，不需要登入或 API Key。

未包含登入、資料庫、Dashboard、AI Memory、MCP、LangGraph、推播或外部整合。
