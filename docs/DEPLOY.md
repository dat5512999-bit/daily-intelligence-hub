# 部署手冊

Sprint 1 是本機命令列工具，無伺服器部署需求。若要每日產生，可在作業系統排程器建立工作：工作目錄設為專案根目錄，命令為 `python main.py --live`。

若作業系統沒有將 Python 加入 PATH，請在排程器使用 Python 的完整路徑。

## GitHub Pages 每 30 分鐘更新

專案內的 `.github/workflows/daily-report.yml` 在每小時第 17 與第 47 分鐘安排 Live Mode，成功後部署到 GitHub Pages。這是排程時段，不是準時完成的承諾；可能延遲，實際完成時間以 Actions 與頁首最後檢查為準。

若要立即更新：GitHub 專案 → **Actions** → **Daily Intelligence Report** → **Run workflow**。確認最新執行是綠色成功後，再重新整理 Pages 網址。

0.9.21 起，報告頁首的「手動產生新報告」可直接帶你到上述 Actions 頁；「檢查最新頁面」只負責重新整理已部署結果。基於安全性，公開網頁不會內嵌 GitHub 權杖，因此仍需在已登入的 GitHub 頁面按一次 **Run workflow**。

如果上傳新版本後仍沒有每 30 分鐘執行，請直接檢查 GitHub 上的 `.github/workflows/daily-report.yml`。它必須包含 `cron: "17,47 * * * *"`；若仍是 `cron: "0 0 * * *"`，代表隱藏的 `.github` 資料夾沒有隨一般網頁上傳更新。

0.9.24 執行命令為 `python main.py --live --restore-published-state`。必須上傳 `app/output/feedback.js`，renderer 會把它內嵌到報告。完整部署 `reports/`，包含新產生的 `state.json`。第一次部署沒有上一份比較紀錄時是正常狀態；下一輪開始比較。靜態 state.json 只含公開文章雜湊，不含手機收藏。

main 分支更新也會觸發部署；部署前先執行 Python 驗收測試，失敗時停止發布。分支上傳完成後一次合併，避免線上使用半套程式。
