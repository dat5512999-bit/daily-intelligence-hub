@echo off
setlocal
set "CODEX_PYTHON=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
where python >nul 2>nul
if %errorlevel% equ 0 (
    python main.py --demo
) else if exist "%CODEX_PYTHON%" (
    "%CODEX_PYTHON%" main.py --demo
) else (
    echo 找不到 Python，請安裝 Python 3.9 或更新版本。
    pause
    exit /b 1
)
start "" "reports\preview.html"
