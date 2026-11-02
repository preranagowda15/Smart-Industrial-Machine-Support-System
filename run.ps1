Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "Starting Manufacturing Manual Assistant (Django + RAG)" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

$pythonExe = ".\venv\Scripts\python.exe"
if (-not (Test-Path $pythonExe)) {
    $pythonExe = "python"
}

Write-Host "`n[1/3] Applying database migrations..." -ForegroundColor Yellow
& $pythonExe manage.py migrate --noinput

Write-Host "`n[2/3] Seeding demo users and machine manuals..." -ForegroundColor Yellow
& $pythonExe scripts/seed_data.py

Write-Host "`n[3/3] Opening browser at http://127.0.0.1:8000/ ..." -ForegroundColor Green
Start-Process "http://127.0.0.1:8000/"

Write-Host "`n========================================================" -ForegroundColor Cyan
Write-Host "Server running at http://127.0.0.1:8000/" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the server." -ForegroundColor Gray
Write-Host "========================================================`n" -ForegroundColor Cyan

& $pythonExe manage.py runserver 127.0.0.1:8000
