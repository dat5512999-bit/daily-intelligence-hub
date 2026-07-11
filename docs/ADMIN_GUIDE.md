# 管理者手冊

Sprint 1 不儲存帳號、Cookie、資料庫或 API 金鑰。來源為公開端點。新增來源時，於 `app/sources/` 建立符合 `Source` Protocol 的類別，並在 `main.py` 的 Live 清單註冊；同時增加測試與本文件。

報告品質門檻由 `DailyReport.health_label` 管理：來源少於 3 個為「資訊來源不足」，有來源錯誤但仍有足夠資料為「部分來源受限」。不得把來源錯誤隱藏或以範例資料補足 Live 報告。
