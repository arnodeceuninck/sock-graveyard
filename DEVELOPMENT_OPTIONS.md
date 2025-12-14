# 🧦 Sock Graveyard - Development Options

## Two Ways to Run the Project

### 🚀 Option 1: Local Development (Fast!)

**Perfect for:** Active development, testing, quick iterations

**Advantages:**
- ⚡ Starts in 10 seconds (vs 5-15 minutes for Docker)
- 🔄 Hot reload - see changes instantly
- 💾 Uses ~500MB RAM (vs ~4GB for Docker)
- 🐛 Easy debugging
- 📝 Simple logs

**Quick Start:**
```powershell
# One-time setup
.\setup_local_dev.ps1

# Run everything
.\run_local_dev.ps1
```

**Access:**
- Backend API: http://localhost:8000/docs
- Frontend: Opens automatically

**See:** `LOCAL_QUICKSTART.md` for details

---

### 🐳 Option 2: Docker (Production-Like)

**Perfect for:** Production testing, deployment, full environment

**Advantages:**
- 🏗️ Complete production environment
- 🗄️ PostgreSQL with pgvector
- 🔴 Redis caching
- 🌐 Nginx reverse proxy
- 📦 Isolated containers

**Quick Start:**
```bash
docker compose up --build
```

**Access:**
- Backend API: http://localhost:8000/docs
- Frontend: http://localhost:19006

**See:** Main README for Docker setup

---

## Comparison

| Feature | Local | Docker |
|---------|-------|--------|
| **Startup Time** | 10 sec | 5-15 min |
| **RAM Usage** | ~500MB | ~4GB |
| **Hot Reload** | ✅ Instant | ❌ Rebuild |
| **Database** | SQLite | PostgreSQL |
| **Caching** | None | Redis |
| **Best For** | Development | Production Testing |

---

## Which Should I Use?

### Use **Local Development** when:
- 🛠️ Writing code and testing changes
- 🐛 Debugging issues
- 🧪 Running quick tests
- 💻 Limited system resources
- ⚡ Need fast feedback

### Use **Docker** when:
- 🚀 Deploying to production
- 🧪 Testing full stack integration
- 📊 Need PostgreSQL-specific features
- 🔴 Testing with Redis caching
- 🌐 Testing with Nginx

---

## Can I Use Both?

Yes! They're completely independent:

```powershell
# Develop locally during the day
.\run_local_dev.ps1
# ... make changes, test quickly ...

# Test with Docker before committing
docker compose up --build
# ... verify everything works in production environment ...
```

Local uses `sock_graveyard_local.db`, Docker uses PostgreSQL container. No conflicts!

---

## Documentation

- **`LOCAL_QUICKSTART.md`** - 2-minute local setup guide
- **`LOCAL_DEV_GUIDE.md`** - Complete local development guide
- **`LOCAL_SETUP_SUMMARY.md`** - Technical details
- **`README.md`** - Docker setup and deployment
- **`LOCAL_TESTING.md`** - Algorithm testing guide

---

## Quick Command Reference

### Local Development
```powershell
.\setup_local_dev.ps1              # One-time setup
.\run_local_dev.ps1                # Start everything
python run_backend_local.py        # Backend only
.\run_frontend_local.ps1           # Frontend only
python local_test_matching.py ...  # Test matching
```

### Docker
```bash
docker compose up --build          # Start everything
docker compose down                # Stop everything
docker compose logs -f backend     # View logs
docker compose exec backend bash   # Access container
```

---

## Need Help?

1. **Local dev issues?** → See `LOCAL_DEV_GUIDE.md` troubleshooting section
2. **Docker issues?** → See main `README.md` troubleshooting section
3. **Testing issues?** → See `LOCAL_TESTING.md`
4. **Backend issues?** → Check API docs at `/docs`

---

**Recommendation:** Start with local development for daily work, use Docker for final testing before deployment. 🎯
