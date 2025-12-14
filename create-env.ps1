# Create a simple .env file with a generated secret
$secretBytes = New-Object byte[] 32
[System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($secretBytes)
$secretKey = [System.Convert]::ToBase64String($secretBytes)

$envContent = @"
# Database Configuration
DATABASE_URL=postgresql://sockuser:sockpassword@db:5432/sockgraveyard

# Redis Configuration
REDIS_URL=redis://redis:6379

# JWT Configuration (auto-generated secure key)
SECRET_KEY=$secretKey
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Environment
ENVIRONMENT=development

# Backend URL (for frontend)
BACKEND_URL=http://localhost:80
"@

Set-Content -Path ".env" -Value $envContent
Write-Host "✓ .env file created with secure secret key" -ForegroundColor Green
