# 安裝手冊

0.9.29 不新增套件、資料庫、登入或 API Key。新番、Netflix、Disney+ 沿用既有公開 RSS 更新流程；Live 報告可從少量 Google News 文章出版頁讀取來源提供的預覽圖；每日充電由內建原創內容輪替；收藏由報告內嵌的 `app/output/feedback.js` 在瀏覽器本機儲存。圖片擷取是盡力而為；來源拒絕或無圖時仍可正常使用文字報告。

1. 安裝 [Python](https://www.python.org/downloads/) 3.9+，安裝時選擇加入 PATH。
2. 解壓或複製本專案。
3. 在專案目錄執行 `python main.py --demo`。

本 Sprint 無第三方套件，因此不需 `pip install`。

0.9.24 仍使用同樣啟動方式。HTML 內嵌互動程式，雙擊 `reports/preview.html` 即可使用；收藏與偏好需要瀏覽器允許本機儲存，若被限制會顯示暫存提示。

## 0.9.25｜GitHub 使用指南與冷知識（2026-10-07）

0.9.25 沿用原 Python 環境及標準函式庫；沒有新增套件或 API Key。更新後執行 python main.py --demo，即可離線預覽 GitHub 指南與冷知識。

限制：GitHub 使用例子是用途分類說明，非全文翻譯、實測或免費使用保證；冷知識目前六則每日輪替三則，非即時新聞。未引入資料庫、登入或付費服務。
