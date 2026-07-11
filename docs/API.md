# API 文件

Sprint 1 沒有 HTTP API。內部擴充介面為：

```python
class Source(Protocol):
    name: str
    def fetch(self) -> list[IntelligenceItem]: ...
```

來源輸出會被正規化、過濾、聚類、排名後交給 renderer。
