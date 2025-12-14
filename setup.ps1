# Quick Setup Script for Windows PowerShell

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  SOCK GRAVEYARD - SETUP SCRIPT" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is installed
Write-Host "Checking for Docker..." -ForegroundColor Yellow
$dockerVersion = docker --version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}
Write-Host "✓ Docker found: $dockerVersion" -ForegroundColor Green

# Check if Docker Compose is available
Write-Host "Checking for Docker Compose..." -ForegroundColor Yellow
$composeVersion = docker-compose --version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker Compose is not installed" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Docker Compose found: $composeVersion" -ForegroundColor Green

# Create .env file if it doesn't exist
if (-Not (Test-Path ".env")) {
    Write-Host ""
    Write-Host "Creating .env file..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    
    # Generate a random secret key
    $bytes = New-Object byte[] 32
    [System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
    $secretKey = [System.Convert]::ToBase64String($bytes)
    
    # Replace the secret key in .env
    $envContent = Get-Content ".env"
    $envContent = $envContent -replace "your-secret-key-change-in-production-use-openssl-rand-hex-32", $secretKey
    Set-Content ".env" $envContent
    
    Write-Host "✓ .env file created with secure secret key" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "✓ .env file already exists" -ForegroundColor Green
}

# Create necessary directories
Write-Host ""
Write-Host "Creating directories..." -ForegroundColor Yellow
$dirs = @("backend/logs", "backend/images")
foreach ($dir in $dirs) {
    if (-Not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}
Write-Host "✓ Directories created" -ForegroundColor Green

# Start Docker containers
Write-Host ""
Write-Host "Starting Docker containers..." -ForegroundColor Yellow
Write-Host "This may take a few minutes on first run..." -ForegroundColor Cyan
docker-compose up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Containers started successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to start containers" -ForegroundColor Red
    exit 1
}

# Wait for services to be ready
Write-Host ""
Write-Host "Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check if backend is responding
Write-Host "Checking backend health..." -ForegroundColor Yellow
$maxRetries = 30
$retryCount = 0
$backendReady = $false

while ($retryCount -lt $maxRetries -and -not $backendReady) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost/health" -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $backendReady = $true
        }
    } catch {
        $retryCount++
        Write-Host "  Waiting... (attempt $retryCount/$maxRetries)" -ForegroundColor Gray
        Start-Sleep -Seconds 2
    }
}

if ($backendReady) {
    Write-Host "✓ Backend is healthy and responding" -ForegroundColor Green
} else {
    Write-Host "⚠ Backend might still be starting up. Please check logs with: docker-compose logs -f backend" -ForegroundColor Yellow
}

# Display summary
Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  SETUP COMPLETE!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Services running:" -ForegroundColor White
Write-Host "  • API: http://localhost/api" -ForegroundColor Gray
Write-Host "  • API Docs: http://localhost/docs" -ForegroundColor Gray
Write-Host "  • Health: http://localhost/health" -ForegroundColor Gray
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host "  1. Open http://localhost/docs in your browser" -ForegroundColor Gray
Write-Host "  2. Test the API endpoints" -ForegroundColor Gray
Write-Host "  3. Set up the frontend (see frontend/SETUP.md)" -ForegroundColor Gray
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor White
Write-Host "  • View logs:      docker-compose logs -f" -ForegroundColor Gray
Write-Host "  • Stop services:  docker-compose down" -ForegroundColor Gray
Write-Host "  • Restart:        docker-compose restart" -ForegroundColor Gray
Write-Host "  • Run tests:      docker-compose exec backend pytest tests/ -v" -ForegroundColor Gray
Write-Host ""
Write-Host "Happy sock matching! 🧦✨" -ForegroundColor Cyan
