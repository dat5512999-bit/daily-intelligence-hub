@echo off
setlocal

where python >nul 2>nul
if %errorlevel% equ 0 (
    python main.py --live
) else (
    set "CODEX_PYTHON=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
    if exist "%CODEX_PYTHON%" (
        "%CODEX_PYTHON%" main.py --live
    ) else (
        echo 找不到 Python，請安裝 Python 3.9 或更新版本。
    )
)

if exist "reports\preview.html" start "" "reports\preview.html"
