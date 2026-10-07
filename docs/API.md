# API 文件

Sprint 1 沒有 HTTP API。內部擴充介面為：

```python
class Source(Protocol):
    name: str
    def fetch(self) -> list[IntelligenceItem]: ...
```

來源輸出會被正規化、過濾、聚類、排名後交給 renderer。

`DailyReport` 另提供 `source_count`、`health_label`、`health_note`，輸出層必須使用這些欄位提示資料品質，不得自行假設 Live Mode 就代表全部來源成功。

`IntelligenceCluster.image_url` 目前只對 YouTube 影片產生官方縮圖；其他來源回傳空字串。

## 0.9.24 更新狀態與偏好

`DailyReport` 新增 `last_content_change_at`、`new_item_count`、`changed_item_count`、`comparison_available`。`compare_report(report, previous)` 回傳新 report 與 schema 1 snapshot。

公開靜態 `state.json` 包含 `checked_at`、`last_content_change_at`、`fingerprints`，最多 500 個文章 ID 與內容摘要雜湊；不是執行指令的 API，不含瀏覽器偏好或金鑰。時間均使用 ISO 8601，HTML 轉為台灣時間。

CLI 新增 `--restore-published-state`，只在 Live 模式讀取此專案的公開比較紀錄。Demo 使用獨立 `demo-state.json`，不連網。

`topic_for(title)` 對具名主題回傳標籤；無法識別時不提供主題偏好。瀏覽器 localStorage key 為 `daily-intelligence-preferences-v3`，包含單篇 `saved`、`hidden` 與主題 `topics`。收藏 ID 不依畫面位置變動。

## 0.9.25｜GitHub 使用指南與冷知識（2026-10-07）

IntelligenceItem 新增 repo_description: str = ''，保留作者簡介供用途分類。repository_guide(cluster) 回傳 RepositoryGuide（purpose、example、steps、audience、evidence、matched）。KnowledgeSource(day: date | None) 符合 Source.fetch，離線回傳三則固定查核日期的資料。未加入網頁服務或外部 API。

限制：GitHub 使用例子是用途分類說明，非全文翻譯、實測或免費使用保證；冷知識目前六則每日輪替三則，非即時新聞。未引入資料庫、登入或付費服務。
