# 部署手冊

Sprint 1 是本機命令列工具，無伺服器部署需求。若要每日產生，可在作業系統排程器建立工作：工作目錄設為專案根目錄，命令為 `python main.py --live`。

若作業系統沒有將 Python 加入 PATH，請在排程器使用 Python 的完整路徑。

## GitHub Pages 每小時更新

專案內的 `.github/workflows/daily-report.yml` 會在 GitHub Actions 於每小時約第 17 分鐘執行一次 Live Mode，成功後部署到 GitHub Pages。這是固定時刻，不是從手動更新起算 60 分鐘；GitHub 可能延後數分鐘，Pages 也可能需要 1 至 3 分鐘快取更新。

若要立即更新：GitHub 專案 → **Actions** → **Daily Intelligence Report** → **Run workflow**。確認最新執行是綠色成功後，再重新整理 Pages 網址。
