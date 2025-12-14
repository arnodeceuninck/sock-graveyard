# Quick setup script for local development

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "SOCK GRAVEYARD - LOCAL DEVELOPMENT SETUP" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

$scriptDir = $PSScriptRoot

# Check Python
Write-Host "Checking prerequisites..." -ForegroundColor Cyan
Write-Host ""

$pythonCmd = "python"
try {
    $pythonVersion = & $pythonCmd --version 2>&1
    Write-Host "[OK] Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python not found. Please install Python 3.8+ from python.org" -ForegroundColor Red
    exit 1
}

# Check Node.js
try {
    $nodeVersion = & node --version 2>&1
    Write-Host "[OK] Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "[WARN] Node.js not found. Install from nodejs.org to run frontend" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "BACKEND SETUP" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Check for virtual environment
$venvPath = Join-Path $scriptDir ".venv"
if (-not (Test-Path $venvPath)) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
    & $pythonCmd -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
    Write-Host "[OK] Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "[OK] Virtual environment exists" -ForegroundColor Green
}

# Activate and install dependencies
Write-Host ""
Write-Host "Installing backend dependencies..." -ForegroundColor Yellow
$pipExe = Join-Path $venvPath "Scripts\pip.exe"

# Install backend requirements
& $pipExe install -r backend/requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARN] Some packages failed to install" -ForegroundColor Yellow
}

# Install additional local dev packages
Write-Host "Installing local development packages..." -ForegroundColor Yellow
& $pipExe install uvicorn[standard] aiosqlite python-dotenv
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Backend dependencies installed" -ForegroundColor Green
} else {
    Write-Host "[WARN] Some packages failed to install" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "FRONTEND SETUP" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

$frontendDir = Join-Path $scriptDir "frontend"
if (Test-Path $frontendDir) {
    Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
    Set-Location $frontendDir
    
    # Check if package.json exists
    if (Test-Path "package.json") {
        npm install
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] Frontend dependencies installed" -ForegroundColor Green
        } else {
            Write-Host "[WARN] Frontend installation had errors" -ForegroundColor Yellow
        }
    } else {
        Write-Host "[WARN] No package.json found in frontend/" -ForegroundColor Yellow
    }
    
    Set-Location $scriptDir
} else {
    Write-Host "[WARN] Frontend directory not found" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "CONFIGURATION" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Setup .env file
$envFile = Join-Path $scriptDir ".env"
$envLocalFile = Join-Path $scriptDir ".env.local"

if (-not (Test-Path $envFile)) {
    if (Test-Path $envLocalFile) {
        Write-Host "Creating .env from .env.local..." -ForegroundColor Yellow
        Copy-Item $envLocalFile $envFile
        Write-Host "[OK] .env file created" -ForegroundColor Green
    } else {
        Write-Host "[WARN] No .env.local template found" -ForegroundColor Yellow
        Write-Host "Creating minimal .env file..." -ForegroundColor Yellow
        
        @"
DATABASE_URL=sqlite:///./sock_graveyard_local.db
SECRET_KEY=local-dev-secret-key-change-in-production
ENVIRONMENT=development
UPLOAD_DIR=images_local
VITE_API_URL=http://localhost:8000
"@ | Out-File -FilePath $envFile -Encoding utf8
        
        Write-Host "[OK] Minimal .env file created" -ForegroundColor Green
    }
} else {
    Write-Host "[OK] .env file already exists" -ForegroundColor Green
}

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Green
Write-Host "SETUP COMPLETE!" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host ""
Write-Host "   Run everything:" -ForegroundColor White
Write-Host "   .\run_local_dev.ps1" -ForegroundColor Yellow
Write-Host ""
Write-Host "   Or run services separately:" -ForegroundColor White
Write-Host "   python run_backend_local.py      # Backend API" -ForegroundColor Yellow
Write-Host "   .\run_frontend_local.ps1          # Frontend" -ForegroundColor Yellow
Write-Host ""
Write-Host "   Test matching algorithm:" -ForegroundColor White
Write-Host "   python local_test_matching.py sample_images/*.jpg" -ForegroundColor Yellow
Write-Host ""
Write-Host "Documentation:" -ForegroundColor Cyan
Write-Host "   See LOCAL_DEV_GUIDE.md for detailed instructions" -ForegroundColor White
Write-Host ""
