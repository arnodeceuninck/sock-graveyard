# Run both backend and frontend locally
# This script starts both servers in separate windows

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "SOCK GRAVEYARD - LOCAL DEVELOPMENT ENVIRONMENT" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

$scriptDir = $PSScriptRoot

# Check if Python virtual environment exists
$venvPath = Join-Path $scriptDir ".venv"
if (-not (Test-Path $venvPath)) {
    Write-Host "[WARN] Virtual environment not found at $venvPath" -ForegroundColor Yellow
    Write-Host "[INFO] Create it with: python -m venv .venv" -ForegroundColor Cyan
    Write-Host "[INFO] Then install backend dependencies: .venv\Scripts\pip install -r backend/requirements.txt" -ForegroundColor Cyan
    exit 1
}

# Check if .env file exists
$envFile = Join-Path $scriptDir ".env"
$envLocalFile = Join-Path $scriptDir ".env.local"
if (-not (Test-Path $envFile)) {
    if (Test-Path $envLocalFile) {
        Write-Host "[INFO] Copying .env.local to .env" -ForegroundColor Cyan
        Copy-Item $envLocalFile $envFile
    } else {
        Write-Host "[WARN] No .env file found. Using defaults." -ForegroundColor Yellow
    }
}

Write-Host "[OK] Environment configured" -ForegroundColor Green
Write-Host ""
Write-Host "Starting services..." -ForegroundColor Cyan
Write-Host "   Backend API: http://localhost:8000" -ForegroundColor Yellow
Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "   Frontend: Will open in browser/Expo" -ForegroundColor Yellow
Write-Host ""

# Start backend in new window
Write-Host "Starting backend server..." -ForegroundColor Cyan
$pythonExe = Join-Path $venvPath "Scripts\python.exe"
$backendScript = Join-Path $scriptDir "run_backend_local.py"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& '$pythonExe' '$backendScript'"

# Wait a bit for backend to start
Start-Sleep -Seconds 3

# Start frontend in new window
Write-Host "Starting frontend server..." -ForegroundColor Cyan
$frontendScript = Join-Path $scriptDir "run_frontend_local.ps1"
Start-Process powershell -ArgumentList "-NoExit", "-File", "$frontendScript"

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Green
Write-Host "[OK] Both servers are starting in separate windows" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "   1. Wait for both servers to start (check the new windows)" -ForegroundColor White
Write-Host "   2. Backend API: http://localhost:8000/docs" -ForegroundColor White
Write-Host "   3. Frontend: Follow instructions in the Expo window" -ForegroundColor White
Write-Host "   4. Close the PowerShell windows to stop the servers" -ForegroundColor White
Write-Host ""
Write-Host "Tip: Use 'python local_test_matching.py' to test matching without the web UI" -ForegroundColor Yellow
Write-Host ""
