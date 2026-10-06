# 備份與還原手冊

備份整個專案資料夾，特別是 `config/`、`.github/workflows/` 與設定檔。0.9.24 起另備份 `reports/state.json`，才能保留更新比較歷史；缺少它不會阻止執行，但會重新建立基準。Demo 紀錄為 `reports/demo-state.json`，與 Live 分開。

收藏與主題偏好存在同一台手機的瀏覽器，清除網站資料或更換裝置會遺失，目前沒有跨裝置備份。不要以網站報告備份代替收藏備份。

程式回復時，在 GitHub 找到本次發布前的 commit，還原本次變更的檔案並重新執行工作流程；不要只還原 VERSION。還原後先執行 `python main.py --demo` 及測試，再發布。0.9.24 發布前版本為 0.9.23，commit：`4329d413815e260e27823206065c3ce9ca9c380d`。
