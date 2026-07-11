# API 文件

Sprint 1 沒有 HTTP API。內部擴充介面為：

```python
class Source(Protocol):
    name: str
    def fetch(self) -> list[IntelligenceItem]: ...
```

來源輸出會被正規化、過濾、聚類、排名後交給 renderer。

`DailyReport` 另提供 `source_count`、`health_label`、`health_note`，輸出層必須使用這些欄位提示資料品質，不得自行假設 Live Mode 就代表全部來源成功。

`IntelligenceCluster.image_url` 是呈現層的安全圖片提示。目前只會對 YouTube 影片產生官方縮圖網址、對 GitHub Trending 產生 Owner Avatar；未知來源會回傳空字串，讓輸出層維持無圖片。
