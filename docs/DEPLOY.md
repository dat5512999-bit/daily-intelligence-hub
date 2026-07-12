# 部署手冊

Sprint 1 是本機命令列工具，無伺服器部署需求。若要每日產生，可在作業系統排程器建立工作：工作目錄設為專案根目錄，命令為 `python main.py --live`。

若作業系統沒有將 Python 加入 PATH，請在排程器使用 Python 的完整路徑。

## GitHub Pages 每 30 分鐘更新

專案內的 `.github/workflows/daily-report.yml` 會在 GitHub Actions 於每小時約第 17 與第 47 分鐘各執行一次 Live Mode，成功後部署到 GitHub Pages。這是固定時刻，不是從手動更新起算 30 分鐘；GitHub 可能延後數分鐘，Pages 也可能需要 1 至 3 分鐘快取更新。

若要立即更新：GitHub 專案 → **Actions** → **Daily Intelligence Report** → **Run workflow**。確認最新執行是綠色成功後，再重新整理 Pages 網址。

0.9.21 起，報告頁首的「手動產生新報告」可直接帶你到上述 Actions 頁；「檢查最新頁面」只負責重新整理已部署結果。基於安全性，公開網頁不會內嵌 GitHub 權杖，因此仍需在已登入的 GitHub 頁面按一次 **Run workflow**。

如果上傳新版本後仍沒有每 30 分鐘執行，請直接檢查 GitHub 上的 `.github/workflows/daily-report.yml`。它必須包含 `cron: "17,47 * * * *"`；若仍是 `cron: "0 0 * * *"`，代表隱藏的 `.github` 資料夾沒有隨一般網頁上傳更新。
