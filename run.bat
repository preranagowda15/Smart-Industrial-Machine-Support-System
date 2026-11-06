@echo off
title Industrial AI Platform (Plate Inspection & Maintenance Assistant)
cd /d "%~dp0"

echo =========================================================
echo Starting Industrial AI Platform (Round 1 & Round 2 Unified)
echo Visual Plate Inspection (CV) + AI Maintenance Assistant (RAG)
echo =========================================================

REM Activate virtual environment
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else if exist "..\venv\Scripts\activate.bat" (
    call ..\venv\Scripts\activate.bat
) else (
    echo [INFO] Running with system python environment.
)

REM Run database migrations
echo [1/3] Checking database migrations...
python manage.py migrate --no-input

REM Seed demo accounts
echo [2/3] Verifying demonstration users and manuals...
python scripts/seed_data.py

REM Open browser automatically after Django is reachable
echo [3/3] Opening browser at http://127.0.0.1:8000/login/ ...
start "" powershell.exe -NoProfile -Command "$u='http://127.0.0.1:8000/login/'; for($i=0;$i -lt 60;$i++){try{if((Invoke-WebRequest -Uri $u -UseBasicParsing -TimeoutSec 2).StatusCode -eq 200){Start-Process $u; break}}catch{Start-Sleep -Milliseconds 500}}"

echo.
echo =========================================================
echo Server is running at http://127.0.0.1:8000/
echo.
echo Unified Access:
echo   - Visual Plate Inspection: http://127.0.0.1:8000/upload/
echo   - AI Maintenance Assistant: http://127.0.0.1:8000/assistant/
echo.
echo Demo Users:
echo   - Operator:   operator1       / Operator123!
echo   - Engineer:   engineer_demo   / EngineerDemo!2026
echo   - Supervisor: supervisor1     / Supervisor123!
echo   - Admin:      admin1          / Admin123!
echo.
echo Press Ctrl+C in this terminal window to stop the server.
echo =========================================================
echo.

python manage.py runserver 127.0.0.1:8000
pause
