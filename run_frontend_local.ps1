# Run the React Native / Expo frontend locally
# This script starts the Expo development server

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "SOCK GRAVEYARD - LOCAL FRONTEND SERVER" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

$frontendDir = Join-Path $PSScriptRoot "frontend"

# Check if frontend directory exists
if (-not (Test-Path $frontendDir)) {
    Write-Host "[ERROR] Frontend directory not found: $frontendDir" -ForegroundColor Red
    exit 1
}

# Check if node_modules exists
$nodeModules = Join-Path $frontendDir "node_modules"
if (-not (Test-Path $nodeModules)) {
    Write-Host "[WARN] node_modules not found. Installing dependencies..." -ForegroundColor Yellow
    Write-Host ""
    Set-Location $frontendDir
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Failed to install dependencies" -ForegroundColor Red
        exit 1
    }
}

# Check for .env file
$envFile = Join-Path $PSScriptRoot ".env"
if (-not (Test-Path $envFile)) {
    Write-Host "[WARN] No .env file found. Make sure backend URL is configured." -ForegroundColor Yellow
    Write-Host "[INFO] Copy .env.local to .env and adjust if needed" -ForegroundColor Cyan
}

Write-Host "[OK] Dependencies installed" -ForegroundColor Green
Write-Host ""
Write-Host "Starting Expo development server..." -ForegroundColor Cyan
Write-Host "Expo Dev Tools will open in your browser" -ForegroundColor Cyan
Write-Host "Scan QR code with Expo Go app to test on your device" -ForegroundColor Cyan
Write-Host "Press 'w' to open in web browser" -ForegroundColor Cyan
Write-Host "Press 'a' for Android emulator (if installed)" -ForegroundColor Cyan
Write-Host "Press 'i' for iOS simulator (Mac only)" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Start Expo
Set-Location $frontendDir
npm start

Write-Host ""
Write-Host "[OK] Frontend server stopped" -ForegroundColor Green
