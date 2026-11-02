@echo off
title Manufacturing Manual Assistant
echo ========================================================
echo Starting Manufacturing Manual Assistant (Django + RAG)
echo ========================================================

if exist venv\Scripts\python.exe (
    set PYTHON=venv\Scripts\python.exe
) else (
    set PYTHON=python
)

echo.
echo [1/3] Applying database migrations...
%PYTHON% manage.py migrate --noinput

echo.
echo [2/3] Seeding demo users and machine manuals...
%PYTHON% scripts/seed_data.py

echo.
echo [3/3] Opening browser at http://127.0.0.1:8000/
start http://127.0.0.1:8000/

echo.
echo ========================================================
echo Server running at http://127.0.0.1:8000/
echo Press Ctrl+C in this window to stop the server.
echo ========================================================
%PYTHON% manage.py runserver 127.0.0.1:8000
pause

