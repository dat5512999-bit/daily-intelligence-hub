# AI Daily Intelligence Research Hub

## 手機自動查看（GitHub Pages）

專案上傳到 GitHub 並啟用 Pages 後，GitHub 會約每小時自動產生最新報告。手機只要開啟你的 Pages 網址，就能看到最新內容，也可以加入手機桌面當作 App 使用。

完整步驟請看 [GitHub Pages 手機使用說明](docs/GITHUB_PAGES_手機使用說明.md)。

每天從 GitHub Trending、Reddit、Hacker News、Google News RSS、Dcard、Google 熱門搜尋與 TikTok 公開趨勢收集公開訊號，整理為可在 3–5 分鐘讀完的 Markdown 與 HTML Daily Intelligence Report。報告更新時間會以台灣時間顯示。

目前定位為「今天紅什麼情報雷達」：新聞用來保底，Google 熱門搜尋、TikTok 與 Reddit 圈內討論用來找出可能要滑社群才會知道的冷門苗頭；生活流行由交通部觀光署公開活動、台中活動查詢與「小紅書 + 餐廳／穿搭／景點／爆紅」等公開搜尋／新聞訊號組成。Dcard 只作為可用就加分的候補，不是手機版必要條件；不做登入式抓取。報告會清楚標示社群訊號不是已查證新聞。短影音標籤會先過濾機器碼、頁面 id 與低上下文標籤，避免普通人看不懂的內容污染報告。頁面採效率情報雜誌設計，上方會顯示情報數、苗頭數、持股數與來源數，並提供分類快速入口；每個頻道最多顯示 3 則內容，相近話題會合併，避免同一件事洗版。

預設個人化主題為 AI／Codex、生活流行、遊戲與電競、動漫、台中即時事件、台中活動與股票市場。遊戲關注包含幻獸帕魯/Palworld、GTA、SF Online、地平線/Forza、魔獸爭霸/Warcraft、寒冰霸權、Steam 與電競話題。動漫關注包含 Re:0、無職轉生、轉生史萊姆、影之強者、海賊王、犬夜叉、火影忍者、我獨自升級、實力至上主義、盾之勇者、進擊巨人、鬼滅、宮崎駿與周邊/聖地巡禮/遊戲/電影。股票關注包含聯電、臻鼎、0050、精材、群創、星宇航空與機器人概念股。排行榜會保留分類平衡，避免整份報告只剩股市或地方新聞。這些主題可在 `config/interests.json` 調整，不需要帳號或 API Key。

手機頁提供「多看這類／少看這類」本機回饋按鈕；目前會先記在同一台手機或瀏覽器，用來清理版面，未來 Sprint 才會設計跨裝置與伺服器端個人化。加入手機主畫面時會使用專用 App 圖示與名稱，不再只顯示瀏覽器預設字卡。

目前版本：`0.9.14`。頁首會顯示「來源正常／部分來源受限／資訊來源不足／資料不足」，不會在只剩少量媒體來源時假裝即時連線正常。每次 Sprint 完成會同步更新 `VERSION` 與 `CHANGELOG.md`；Git commit 可作為可回復版本點。

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
