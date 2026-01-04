# Local Development Setup

For local development with the `/api` prefix, you have two options:

## Option 1: Using nginx (Recommended)

1. **Install nginx** (if not already installed)
   - Windows: Download from https://nginx.org/en/download.html
   - Or use Chocolatey: `choco install nginx`

2. **Configure nginx** 
   - Copy `nginx-dev.conf` to your nginx conf directory
   - Or update your nginx.conf to include it

3. **Start services**
   ```powershell
   # Terminal 1 - Backend
   cd backend
   .\..\venv\Scripts\Activate.ps1
   $env:PYTHONPATH = "C:\Users\arnod\repos\sock-graveyard\backend"
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   
   # Terminal 2 - Frontend  
   cd frontend
   npm start
   
   # Terminal 3 - Nginx
   nginx -c C:\Users\arnod\repos\sock-graveyard\nginx-dev.conf
   ```

4. **Access**: http://localhost (nginx routes to frontend and /api to backend)

## Option 2: Direct API Access (Without nginx)

If you don't want to run nginx locally, update the frontend config temporarily:

```typescript
// frontend/src/config.ts
export const API_BASE_URL = 'http://localhost:8000';
```

Then just run backend and frontend without nginx:
```powershell
# Terminal 1 - Backend
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 - Frontend
cd frontend  
npm start
```

Access: http://localhost:19006

## Docker Development

For a more production-like environment:

```powershell
docker-compose up -d --build
```

Access: http://localhost

This runs everything (PostgreSQL, backend, frontend, nginx) in Docker.
