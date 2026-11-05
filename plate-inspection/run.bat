@echo off
title Plate Inspection System (BIT-PLATE-CV-1.0)
cd /d "%~dp0"

echo =========================================================
echo Starting Plate Inspection System (BIT-PLATE-CV-1.0)
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
python backend/manage.py migrate --no-input

REM Seed demo accounts
echo [2/3] Verifying demonstration users...
python scripts/seed_users.py

REM Open browser automatically
echo [3/3] Opening browser at http://127.0.0.1:8000/login/ ...
start "" "http://127.0.0.1:8000/login/"

echo.
echo =========================================================
echo Server is running at http://127.0.0.1:8000/
echo Demo Users:
echo   - Operator:   operator1   / Operator123!
echo   - Supervisor: supervisor1 / Supervisor123!
echo   - Admin:      admin1      / Admin123!
echo Press Ctrl+C in this terminal window to stop the server.
echo =========================================================
echo.

python backend/manage.py runserver 127.0.0.1:8000
pause

