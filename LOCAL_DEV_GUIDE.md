# Local Development Guide

Run the entire Sock Graveyard application locally without Docker! Perfect for fast development and testing.

## Quick Start (Windows PowerShell)

### Option 1: Run Everything at Once (Easiest!)

```powershell
# Start both backend and frontend in separate windows
.\run_local_dev.ps1
```

This will:
- ✅ Start the backend API on http://localhost:8000
- ✅ Start the frontend Expo server
- ✅ Open both in separate PowerShell windows
- ✅ Use SQLite (no PostgreSQL needed!)
- ✅ Skip Redis (optional for local dev)

### Option 2: Run Services Separately

**Terminal 1 - Backend:**
```powershell
python run_backend_local.py
```

**Terminal 2 - Frontend:**
```powershell
.\run_frontend_local.ps1
```

## Prerequisites

### Backend Requirements
```powershell
# 1. Create virtual environment (if not already created)
python -m venv .venv

# 2. Activate virtual environment
.\.venv\Scripts\Activate.ps1

# 3. Install backend dependencies
pip install -r backend/requirements.txt

# 4. Install additional packages for local dev
pip install uvicorn[standard] aiosqlite
```

### Frontend Requirements
```powershell
# Install Node.js dependencies
cd frontend
npm install
cd ..
```

## Configuration

### 1. Environment Setup

Copy the local environment template:
```powershell
Copy-Item .env.local .env
```

Or create `.env` with these settings:
```bash
# Database - SQLite (no PostgreSQL needed!)
DATABASE_URL=sqlite:///./sock_graveyard_local.db

# JWT Secret
SECRET_KEY=your-secret-key-here-change-in-production

# Optional: Redis (features work without it)
# REDIS_URL=redis://localhost:6379

# File Storage
UPLOAD_DIR=images_local

# API URL for frontend
VITE_API_URL=http://localhost:8000
```

### 2. Database Setup

SQLite database is created automatically on first run! No manual setup needed.

**Optional**: If you want to use PostgreSQL locally:
```bash
# Install PostgreSQL locally, then:
DATABASE_URL=postgresql://user:password@localhost:5432/sockgraveyard
```

## Usage

### Backend Only

Run the FastAPI backend with hot-reload:
```powershell
python run_backend_local.py
```

**Options:**
```powershell
# Custom port
python run_backend_local.py --port 8080

# Bind to all interfaces (accessible from network)
python run_backend_local.py --host 0.0.0.0

# Disable auto-reload
python run_backend_local.py --no-reload
```

**Access:**
- 🌐 API: http://localhost:8000
- 📚 API Docs (Swagger): http://localhost:8000/docs
- 📖 ReDoc: http://localhost:8000/redoc
- ❤️ Health Check: http://localhost:8000/health

### Frontend Only

Run the Expo development server:
```powershell
.\run_frontend_local.ps1
```

**Or manually:**
```powershell
cd frontend
npm start
```

**Access:**
- 💻 **Web**: Press `w` in terminal or go to http://localhost:19006
- 📱 **Mobile**: Scan QR code with Expo Go app
- 🤖 **Android**: Press `a` (requires Android emulator)
- 🍎 **iOS**: Press `i` (requires iOS simulator on Mac)

### Test Matching Algorithm

Test the sock matching without running the full app:
```powershell
# Test a pair
python local_test_matching.py sample_images/sock1.jpg sample_images/sock2.jpg

# Test multiple images
python local_test_matching.py sample_images/*.jpg
```

## Project Structure

```
sock-graveyard/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── routers/             # API endpoints
│   │   ├── services/            # Business logic
│   │   └── models.py            # Database models
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── screens/             # React Native screens
│   │   ├── components/          # Reusable components
│   │   └── services/            # API client
│   └── package.json
├── .env                         # Local configuration
├── run_backend_local.py         # Backend startup script
├── run_frontend_local.ps1       # Frontend startup script
├── run_local_dev.ps1           # Start both servers
└── local_test_matching.py      # CLI testing tool
```

## Features Enabled Locally

### ✅ Works Without External Services
- **SQLite Database**: No PostgreSQL needed
- **File-based Storage**: Uploads saved to `images_local/`
- **JWT Authentication**: Works with local secret key
- **CLIP Embeddings**: Full AI matching
- **Image Processing**: Background removal, cropping
- **API Documentation**: Full Swagger/ReDoc

### ⚠️ Optional Services
- **Redis**: Caching disabled but features still work
- **pgvector**: Vector similarity in SQLite (via numpy)

## Development Workflow

### 1. Make Backend Changes
```powershell
# Backend auto-reloads on file changes!
# Edit files in backend/app/
# Check terminal for reload confirmation
```

### 2. Make Frontend Changes
```powershell
# Frontend auto-reloads via Fast Refresh
# Edit files in frontend/src/
# Changes appear instantly on web/mobile
```

### 3. Test API Changes
```powershell
# Use Swagger UI at http://localhost:8000/docs
# Or use curl/Postman:
curl http://localhost:8000/health
```

### 4. Test Database
```powershell
# SQLite database file: sock_graveyard_local.db
# View with SQLite browser or:
sqlite3 sock_graveyard_local.db
```

## Troubleshooting

### Backend Issues

**Port already in use:**
```powershell
# Use a different port
python run_backend_local.py --port 8001
```

**Missing dependencies:**
```powershell
pip install -r backend/requirements.txt
pip install uvicorn[standard] aiosqlite
```

**Database errors:**
```powershell
# Delete and recreate database
Remove-Item sock_graveyard_local.db
python run_backend_local.py  # Recreates automatically
```

### Frontend Issues

**Metro bundler errors:**
```powershell
cd frontend
# Clear cache and reinstall
Remove-Item -Recurse node_modules
Remove-Item package-lock.json
npm install
npm start -- --clear
```

**Can't connect to backend:**
```powershell
# Check .env has correct backend URL
# Default: VITE_API_URL=http://localhost:8000
```

**Expo Go not connecting:**
```powershell
# Make sure phone and computer are on same WiFi
# Or use web version: press 'w' in terminal
```

## Performance Tips

### Speed Up Backend Startup
```powershell
# Preload CLIP model (first run is slow)
python -c "import open_clip; open_clip.create_model_and_transforms('ViT-B-32', pretrained='openai')"
```

### Speed Up Frontend
```powershell
# Use web version (faster than mobile)
cd frontend
npm start
# Press 'w' for web
```

## Switching Back to Docker

When you're ready to test with Docker:
```powershell
# Stop local servers (close PowerShell windows)
# Then start Docker
docker compose up --build
```

Local and Docker environments are independent - you can switch between them!

## Advantages of Local Development

### 🚀 Speed
- **Backend**: Instant startup (vs 5-15 min Docker build)
- **Frontend**: Fast Refresh (< 1 second)
- **No container overhead**

### 🛠️ Development
- **Hot reload**: Backend and frontend auto-reload
- **Easy debugging**: Direct Python debugging
- **No Docker complexity**

### 💻 Resources
- **Lower RAM usage**: No Docker containers
- **Lower CPU usage**: No virtualization
- **Works without Docker Desktop**

### 🧪 Testing
- **Quick iteration**: Change code → see results instantly
- **Easy database access**: SQLite file you can inspect
- **Simple logs**: Direct console output

## Production Deployment

⚠️ **Local setup is for development only!**

For production, use Docker:
- PostgreSQL with pgvector
- Redis for caching
- Proper secrets management
- HTTPS/SSL
- Container orchestration

```powershell
# Build and deploy with Docker
docker compose -f docker-compose.prod.yml up -d
```

## Summary

```powershell
# Complete local development setup:

# 1. Setup (once)
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
Copy-Item .env.local .env

# 2. Run (every time)
.\run_local_dev.ps1

# 3. Develop
# - Backend: Edit backend/app/, auto-reloads
# - Frontend: Edit frontend/src/, auto-reloads
# - API Docs: http://localhost:8000/docs

# 4. Test
python local_test_matching.py sample_images/*.jpg
```

Happy coding! 🧦✨
