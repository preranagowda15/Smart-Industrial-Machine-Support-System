# Plate Inspection System (BIT-PLATE-CV-1.0) Runner

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host "Starting Plate Inspection System (BIT-PLATE-CV-1.0)" -ForegroundColor Cyan
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
& $VenvPython backend/manage.py migrate --no-input

# Seed demo users
Write-Host "[2/3] Verifying demonstration users..." -ForegroundColor Green
& $VenvPython scripts/seed_users.py

# Launch browser
Write-Host "[3/3] Opening browser at http://127.0.0.1:8000/login/ ..." -ForegroundColor Green
Start-Process "http://127.0.0.1:8000/login/"

Write-Host "`n=========================================================" -ForegroundColor Cyan
Write-Host "Server running at: http://127.0.0.1:8000/" -ForegroundColor Green
Write-Host "Demo Accounts:" -ForegroundColor Yellow
Write-Host "  * Operator:   operator1   / Operator123!" -ForegroundColor White
Write-Host "  * Supervisor: supervisor1 / Supervisor123!" -ForegroundColor White
Write-Host "  * Admin:      admin1      / Admin123!" -ForegroundColor White
Write-Host "Press Ctrl+C to stop the server.`n" -ForegroundColor DarkGray

& $VenvPython backend/manage.py runserver 127.0.0.1:8000

