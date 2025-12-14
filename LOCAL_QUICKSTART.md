# 🚀 Quick Start: Local Development (No Docker!)

**Tired of waiting for Docker?** Run everything locally in seconds!

## One-Command Setup

```powershell
# Run this once to set everything up
.\setup_local_dev.ps1
```

## One-Command Start

```powershell
# Run this every time to start both backend and frontend
.\run_local_dev.ps1
```

That's it! 🎉

## What You Get

- ✅ **Backend API**: http://localhost:8000/docs
- ✅ **Frontend**: Web + Mobile via Expo
- ✅ **SQLite Database**: No PostgreSQL needed!
- ✅ **Hot Reload**: Changes appear instantly
- ✅ **No Docker**: Faster startup, lower resource usage

## Manual Control

Want to run services separately?

```powershell
# Backend only
python run_backend_local.py

# Frontend only
.\run_frontend_local.ps1

# Test matching algorithm
python local_test_matching.py sample_images/*.jpg
```

## Why Use Local Development?

### 🚀 Speed Comparison

| Task | Docker | Local |
|------|--------|-------|
| **First Start** | 5-15 minutes | 10 seconds |
| **Restart** | 1-2 minutes | 2 seconds |
| **Code Change** | Rebuild (~5 min) | Instant |
| **RAM Usage** | ~4GB | ~500MB |

### 💻 Better Developer Experience

- **Instant feedback**: See changes in < 1 second
- **Easy debugging**: Direct Python/Node.js debugging
- **Simple logs**: Plain console output
- **Database access**: SQLite file you can inspect
- **No container complexity**: Just Python and Node.js

## Features

All features work locally:

- ✅ User authentication (JWT)
- ✅ Sock upload and preprocessing
- ✅ AI matching (CLIP embeddings)
- ✅ Background removal
- ✅ Color & pattern detection
- ✅ Similarity search
- ✅ Image storage
- ✅ API documentation

The only difference: SQLite instead of PostgreSQL (but it works the same!)

## Requirements

- **Python 3.8+**: For backend
- **Node.js 16+**: For frontend (optional)
- **Windows**: These scripts are PowerShell

Already have your virtual environment set up? Just run it!

## File Overview

```
sock-graveyard/
├── run_backend_local.py          # 🐍 Start backend
├── run_frontend_local.ps1        # ⚛️  Start frontend  
├── run_local_dev.ps1             # 🚀 Start both
├── setup_local_dev.ps1           # ⚙️  One-time setup
├── local_test_matching.py        # 🧪 Test matching
├── .env.local                    # 📝 Config template
└── LOCAL_DEV_GUIDE.md           # 📚 Full guide
```

## Troubleshooting

**Backend won't start?**
```powershell
pip install uvicorn fastapi sqlalchemy
```

**Frontend won't start?**
```powershell
cd frontend
npm install
```

**Port already in use?**
```powershell
python run_backend_local.py --port 8001
```

## Back to Docker

When you need the full production environment:

```powershell
docker compose up --build
```

Both environments coexist peacefully! Use local for development, Docker for production testing.

## Documentation

- **LOCAL_DEV_GUIDE.md**: Complete local development guide
- **LOCAL_TESTING.md**: Test matching algorithm guide
- **REFACTORING.md**: How we eliminated code duplication

## Summary

```powershell
# Complete workflow:

# 1. Setup (first time only)
.\setup_local_dev.ps1

# 2. Start everything
.\run_local_dev.ps1

# 3. Develop
# - Edit backend/app/     → auto-reloads
# - Edit frontend/src/    → auto-reloads
# - View API docs → http://localhost:8000/docs

# 4. Test
python local_test_matching.py sample_images/*.jpg

# 5. Deploy (when ready)
docker compose up --build
```

Happy hacking! 🧦✨
