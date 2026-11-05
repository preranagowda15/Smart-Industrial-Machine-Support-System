# Industrial AI Platform (Plate Inspection & Maintenance Assistant) Runner

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host "Starting Industrial AI Platform (Round 1 & Round 2 Unified)" -ForegroundColor Cyan
Write-Host "Visual Plate Inspection (CV) + AI Maintenance Assistant (RAG)" -ForegroundColor Cyan
Write-Host "=========================================================" -ForegroundColor Cyan

# Check and activate venv
$VenvPython = Join-Path $ScriptDir "venv\Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    $VenvPython = Join-Path $ScriptDir "..\venv\Scripts\python.exe"
}
if (-not (Test-Path $VenvPython)) {
    $VenvPython = "python"
}

# Run migrations
Write-Host "[1/3] Checking database migrations..." -ForegroundColor Green
& $VenvPython manage.py migrate --no-input

# Seed demo users & manuals
Write-Host "[2/3] Verifying demonstration users and manuals..." -ForegroundColor Green
& $VenvPython scripts/seed_data.py

# Launch browser
Write-Host "[3/3] Opening browser at http://127.0.0.1:8000/login/ ..." -ForegroundColor Green
Start-Process "http://127.0.0.1:8000/login/"

Write-Host "`n=========================================================" -ForegroundColor Cyan
Write-Host "Server running at: http://127.0.0.1:8000/" -ForegroundColor Green
Write-Host "`nUnified Access:" -ForegroundColor Yellow
Write-Host "  * Visual Plate Inspection:   http://127.0.0.1:8000/upload/" -ForegroundColor White
Write-Host "  * AI Maintenance Assistant: http://127.0.0.1:8000/assistant/" -ForegroundColor White
Write-Host "  * Machine Manuals:          http://127.0.0.1:8000/manuals/" -ForegroundColor White
Write-Host "  * Model Evaluation Matrix:  http://127.0.0.1:8000/evaluation/" -ForegroundColor White
Write-Host "`nDemo Accounts:" -ForegroundColor Yellow
Write-Host "  * Operator:   operator1       / Operator123!" -ForegroundColor White
Write-Host "  * Engineer:   engineer_demo   / EngineerDemo!2026" -ForegroundColor White
Write-Host "  * Supervisor: supervisor1     / Supervisor123!" -ForegroundColor White
Write-Host "  * Admin:      admin1          / Admin123!" -ForegroundColor White
Write-Host "`nPress Ctrl+C to stop the server.`n" -ForegroundColor DarkGray

& $VenvPython manage.py runserver 127.0.0.1:8000
