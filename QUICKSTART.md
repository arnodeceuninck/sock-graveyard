# Development Quickstart

## Prerequisites Check

Before starting, ensure you have:

- [ ] Docker Desktop installed and running
- [ ] Node.js 18+ installed
- [ ] Git installed
- [ ] Code editor (VS Code recommended)

## Quick Setup (5 minutes)

### 1. Start Backend

```powershell
# In project root
.\setup.ps1
```

Wait for the script to complete. It will:
- Create necessary directories
- Generate secure secret key
- Start all Docker containers
- Run database migrations
- Perform health checks

### 2. Verify Backend

Open in browser: http://localhost/docs

You should see the API documentation (Swagger UI).

### 3. Start Frontend

```powershell
# In new terminal
cd frontend
npm install
npm start
```

Scan the QR code with Expo Go app on your phone, or:
- Press `i` for iOS simulator
- Press `a` for Android emulator
- Press `w` for web browser

## First API Call

### Register a User

```powershell
curl -X POST http://localhost/api/auth/register `
  -H "Content-Type: application/json" `
  -d '{\"email\":\"test@example.com\",\"username\":\"testuser\",\"password\":\"password123\"}'
```

### Login

```powershell
curl -X POST http://localhost/api/auth/login `
  -F "username=testuser" `
  -F "password=password123"
```

Copy the `access_token` from the response.

### Upload a Sock (replace YOUR_TOKEN)

```powershell
curl -X POST http://localhost/api/socks/ `
  -H "Authorization: Bearer YOUR_TOKEN" `
  -F "file=@path/to/sock.jpg" `
  -F "description=My lost sock"
```

## Development Workflow

### Backend Development

1. **Edit code** in `backend/app/`
2. **Code reloads automatically** (via --reload flag)
3. **View logs**: `docker-compose logs -f backend`
4. **Run tests**: `docker-compose exec backend pytest -v`

### Frontend Development

1. **Edit code** in `frontend/src/`
2. **Hot reload** automatically updates the app
3. **View errors** in terminal or on device
4. **Test on multiple devices** by scanning QR code

### Database Changes

1. **Edit models** in `backend/app/models.py`
2. **Create migration**:
   ```powershell
   docker-compose exec backend alembic revision --autogenerate -m "description"
   ```
3. **Apply migration**:
   ```powershell
   docker-compose exec backend alembic upgrade head
   ```

## Useful Commands

### Docker

```powershell
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend

# Restart service
docker-compose restart backend

# Stop all services
docker-compose down

# Stop and remove volumes (fresh start)
docker-compose down -v

# Rebuild containers
docker-compose up -d --build
```

### Backend

```powershell
# Enter backend container
docker-compose exec backend bash

# Run Python shell
docker-compose exec backend python

# Run tests
docker-compose exec backend pytest tests/ -v

# Run specific test
docker-compose exec backend pytest tests/test_e2e.py::TestE2EWorkflow::test_01_health_check -v

# Check code style
docker-compose exec backend flake8 app/

# Install new package
docker-compose exec backend pip install package-name
docker-compose exec backend pip freeze > requirements.txt
```

### Database

```powershell
# Connect to PostgreSQL
docker-compose exec db psql -U sockuser -d sockgraveyard

# List tables
docker-compose exec db psql -U sockuser -d sockgraveyard -c "\dt"

# Query users
docker-compose exec db psql -U sockuser -d sockgraveyard -c "SELECT * FROM users;"

# Query socks
docker-compose exec db psql -U sockuser -d sockgraveyard -c "SELECT id, user_id, description, is_matched FROM socks;"
```

### Frontend

```powershell
# Clear cache and restart
npx expo start -c

# Install new package
npm install package-name

# Build for production
npm run build

# Run on specific platform
npm run ios
npm run android
npm run web
```

## Testing

### Run All Tests

```powershell
docker-compose exec backend pytest tests/ -v --cov=app
```

### Test Specific Feature

```powershell
# Authentication
docker-compose exec backend pytest tests/test_e2e.py::TestE2EWorkflow::test_02_user_registration -v

# Sock upload
docker-compose exec backend pytest tests/test_e2e.py::TestE2EWorkflow::test_05_upload_sock -v

# Matching
docker-compose exec backend pytest tests/test_e2e.py::TestE2EWorkflow::test_07_search_similar_socks -v
```

### Test Matching Algorithm

```powershell
# With sample images
docker-compose exec backend python test_matching.py sock1.jpg sock2.jpg
```

## Debugging

### Backend Issues

1. **Check logs**: `docker-compose logs backend`
2. **Check health**: `curl http://localhost/health`
3. **Enter container**: `docker-compose exec backend bash`
4. **Check Python errors**: Look for traceback in logs

### Frontend Issues

1. **Check terminal** for compilation errors
2. **Check device/emulator** for runtime errors
3. **Check network** requests in browser dev tools (web)
4. **Clear cache**: `npx expo start -c`

### Database Issues

1. **Check connection**: `docker-compose exec db pg_isready -U sockuser`
2. **View tables**: `docker-compose exec db psql -U sockuser -d sockgraveyard -c "\dt"`
3. **Reset database**: `docker-compose down -v && docker-compose up -d`

## Common Tasks

### Add New API Endpoint

1. Define route in `backend/app/routers/socks.py` (or create new router)
2. Add schema in `backend/app/schemas.py`
3. Test endpoint in Swagger UI
4. Add test in `backend/tests/test_e2e.py`

### Add New Screen

1. Create screen in `frontend/src/screens/NewScreen.tsx`
2. Add route in `frontend/App.tsx`
3. Add navigation in relevant screens
4. Test navigation flow

### Change Theme Colors

1. Edit `frontend/src/constants/theme.ts`
2. Update `Colors.light` and `Colors.dark`
3. Hot reload will apply changes

### Update Database Schema

1. Edit `backend/app/models.py`
2. Create migration: `docker-compose exec backend alembic revision --autogenerate -m "add_field"`
3. Apply: `docker-compose exec backend alembic upgrade head`
4. Update schemas in `backend/app/schemas.py`

## Performance Tips

### Backend

- Use async/await for I/O operations
- Index frequently queried fields
- Use Redis for caching
- Optimize CLIP model loading (done once at startup)

### Frontend

- Use FlatList for long lists
- Implement pagination
- Cache images locally
- Optimize re-renders with React.memo

## Environment Variables

Create `.env` in project root (auto-created by setup script):

```env
# Database
DATABASE_URL=postgresql://sockuser:sockpassword@db:5432/sockgraveyard

# Redis
REDIS_URL=redis://redis:6379

# JWT
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# App
ENVIRONMENT=development
MATCH_THRESHOLD=0.85
```

For frontend, edit `frontend/src/constants/theme.ts`:

```typescript
export const API_BASE_URL = 'http://localhost:80/api';
```

**Note**: For mobile devices, replace `localhost` with your computer's IP address.

## Project Structure Quick Reference

```
backend/app/
├── routers/        # API endpoints (add routes here)
├── services/       # Business logic (add services here)
├── models.py       # Database models (add tables here)
├── schemas.py      # API schemas (add DTOs here)
├── auth.py         # Authentication logic
├── config.py       # Configuration
└── main.py         # FastAPI app

frontend/src/
├── components/     # Reusable UI (add components here)
├── screens/        # App screens (add screens here)
├── services/       # API client (add API calls here)
├── contexts/       # React contexts (add state here)
└── constants/      # App constants (add config here)
```

## Getting Help

- Check logs: `docker-compose logs -f`
- Check API docs: http://localhost/docs
- Check health: http://localhost/health
- Read error messages carefully
- Search existing issues on GitHub

---

**Now you're ready to develop!** 🚀

Start with small changes, test frequently, and commit often. Happy coding! 🧦✨
