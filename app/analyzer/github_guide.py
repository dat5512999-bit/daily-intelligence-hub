"""Evidence-bound Chinese use-case guides, not AI translations or product demos.

Rules match the repository author's description, never the repository name.
Examples explain a tool category; they are not promises of a repo's capabilities.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.domain.models import IntelligenceCluster


@dataclass(frozen=True)
class RepositoryGuide:
    purpose: str
    example: str
    steps: tuple[str, ...]
    audience: str
    evidence: str
    matched: bool


# Specific applications precede broad AI terms to avoid labelling everything AI.
RULES: tuple[tuple[str, str, str, tuple[str, ...], str], ...] = (
    (r"\b(?:reverse engineer|reverse engineering)\b", "分析現有程式的行為與內部結構", "這類工具供開發者研究自己有權檢查的程式，例如了解功能怎麼運作，協助維護；不保證能還原完整原始碼。", ("提供有權分析的程式", "分析行為與結構", "人工核對研究結果"), "比較適合工程師與研究者；只分析合法授權的內容"),
    (r"\b(?:executables porting|porting.{0,40}(?:linux|windows))\b", "協助把程式移到不同作業系統", "這類工具嘗試轉換程式，使它能在其他系統運作。例如研究主機程式移到電腦的相容性；不代表所有遊戲都能玩。", ("準備合法授權的程式", "轉換並處理相容性", "在目標系統測試"), "比較適合工程師；不是下載後就能直接玩主機遊戲，也不提供遊戲檔案"),
    (r"\b(?:text.to.cad|cad)\b", "用文字輔助建立 3D／工程模型", "這類工具可用在產品外型或零件建模；例如先描述形狀，再檢查產出的模型。", ("描述想要的模型", "工具產出模型", "人工檢查尺寸與外型"), "偏向設計／工程使用者；是否能直接線上用，請確認官方說明"),
    (r"\b(?:e2e|end.to.end|automated testing|test automation)\b", "自動檢查網站或程式是否正常", "這類工具可幫團隊檢查登入、購物等流程，減少每次改版都手動重測。", ("設定要測的流程", "執行測試", "查看失敗的步驟"), "比較適合工程師；通常需要設定測試環境"),
    (r"\b(?:browser automation|browser agent|browser.use|automate.{0,20}browser)\b", "讓工具代你操作網頁", "這類工具用於重複的網頁操作；例如依指定流程瀏覽資料。涉及帳號或付款仍需人工確認。", ("指定網頁任務", "工具操作瀏覽器", "確認操作結果"), "通常需要安裝或設定；不代表能突破網站存取限制"),
    (r"\b(?:web crawl|web scrap|crawler|scraping)\b", "把公開網頁整理成可處理的資料", "這類工具可整理公開文章，供搜尋或後續分析使用；不是所有網站都允許擷取。", ("提供公開網址", "擷取可存取內容", "整理文字／資料"), "比較適合工程師；需遵守網站規則"),
    (r"\b(?:coding agent|coding assistant|code assistant)\b", "用 AI 協助修改與理解程式", "這類工具可以輔助程式開發；例如請它說明程式或提出修改，結果仍要測試。", ("提出程式需求", "取得建議／修改", "人工確認與測試"), "偏向程式開發用途；安裝方式與 AI 費用需另確認"),
    (r"\b(?:agent skills|skills for|collection of.{0,30}skills|skill collection)\b", "提供 AI 助手可參考的任務指南", "這類指南把工作方法整理成步驟，讓相容的 AI 助手照著處理；不是下載後就能單獨運作的 App。", ("挑選任務指南", "接到相容 AI 助手", "依指南完成工作"), "需要相容的 AI 工具；不保證免費或免設定"),
    (r"\b(?:image generation|text.to.image)\b", "用文字輔助產生圖片", "這類工具可用於視覺草稿；例如描述海報風格後產生候選圖片，仍需檢查授權與細節。", ("輸入畫面描述", "產生候選圖片", "挑選與修改"), "可能需要模型、顯示卡或外部服務；請先看安裝需求"),
    (r"\b(?:speech.to.text|transcription|transcribe)\b", "把錄音轉成文字", "這類工具可協助整理訪談或會議逐字稿；辨識結果仍要校對人名與專有名詞。", ("提供錄音", "辨識成文字", "校對結果"), "需確認語言支援與錄音隱私；安裝需求依專案而異"),
    (r"\b(?:retrieval.augmented|rag|knowledge base)\b", "從文件中找資料，輔助回答問題", "這類工具適合整理文件後提問；例如從操作手冊找步驟，但答案需對照原文。", ("加入文件", "提出問題", "對照來源確認答案"), "通常需要設定資料來源與模型；不保證免 API Key"),
)


def repository_guide(cluster: IntelligenceCluster) -> RepositoryGuide:
    """Return conservative category guidance backed by source description."""
    evidence = next((item.repo_description for item in cluster.items if item.repo_description.strip()), "")
    for pattern, purpose, example, steps, audience in RULES:
        if evidence and re.search(pattern, evidence, re.IGNORECASE):
            return RepositoryGuide(purpose, example, steps, audience, evidence, True)
    return RepositoryGuide(
        "用途尚無法可靠判讀", "目前介紹不足，先看官方繁中翻譯；不靠專案名稱猜它能做什麼。",
        (), "尚未確認安裝方式、費用與使用門檻", evidence, False,
    )
