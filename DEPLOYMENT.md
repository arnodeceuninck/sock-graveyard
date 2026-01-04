# Sock Graveyard - Docker Deployment Guide

## Prerequisites

- Docker and Docker Compose installed
- Cloudflare Tunnel configured for `socks.arnodece.com`

## Quick Start

1. **Create environment file**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` file with your settings**
   - Set a secure `POSTGRES_PASSWORD`
   - Generate a strong `SECRET_KEY` (at least 32 characters)
   - Update `DATABASE_URL` with the same password

3. **Build and start services**
   ```bash
   docker-compose up -d --build
   ```

4. **Check service status**
   ```bash
   docker-compose ps
   docker-compose logs -f
   ```

## Services

The stack includes:

- **PostgreSQL** (port 5432): Database
- **Backend**: FastAPI application
- **Frontend**: Expo/React web application
- **Nginx** (port 80): Reverse proxy
- **Alembic**: Database migrations (runs once on startup)

## Service URLs

- Full application: http://localhost
- Backend API: http://localhost/api
- Frontend: http://localhost

## Cloudflare Tunnel Setup

Configure your Cloudflare Tunnel to point `socks.arnodece.com` to `localhost:80` on your server.

Example tunnel config:
```yaml
tunnel: your-tunnel-id
credentials-file: /path/to/credentials.json

ingress:
  - hostname: socks.arnodece.com
    service: http://localhost:80
  - service: http_status:404
```

## Data Persistence

Two volumes are created for data persistence:

- `postgres-data`: Database files
- `uploads`: User-uploaded sock images

## Useful Commands

### View logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f nginx
```

### Restart services
```bash
docker-compose restart
```

### Stop services
```bash
docker-compose down
```

### Rebuild after code changes
```bash
docker-compose up -d --build
```

### Access database
```bash
docker-compose exec postgres psql -U postgres -d sock_graveyard
```

### Run migrations manually
```bash
docker-compose exec backend alembic upgrade head
```

### Clean up everything (including data)
```bash
docker-compose down -v
```

## Troubleshooting

### Backend won't start
- Check database connection: `docker-compose logs postgres`
- Verify environment variables in `.env`
- Check migrations: `docker-compose logs alembic-migration`

### Frontend can't reach backend
- Check nginx configuration: `docker-compose logs nginx`
- Verify nginx routes requests to `/api` correctly
- Check backend is running: `docker-compose ps backend`

### Images not loading
- Verify uploads volume is mounted: `docker volume ls`
- Check backend logs for file upload errors
- Ensure upload directory has correct permissions

## Production Considerations

1. **Security**
   - Change default passwords in `.env`
   - Use strong SECRET_KEY
   - Consider adding SSL/TLS (though Cloudflare provides this)

2. **Backups**
   - Regularly backup `postgres-data` volume
   - Backup `uploads` volume

3. **Monitoring**
   - Set up log aggregation
   - Monitor disk usage for uploads
   - Track database size

4. **Updates**
   - Pull latest code: `git pull`
   - Rebuild: `docker-compose up -d --build`
   - Check migrations run successfully


## APK
Current test api made with these settings:
```
# Install EAS CLI if you haven't
npm install -g eas-cli

# Login to your Expo account
npx eas-cli login

# Configure EAS Build
npx eas-cli build:configure

# Build for Android (production)
npx eas-cli build --platform android --profile production
```
Somehow eas-cli randomly adds audio record permission, corresponds to this issue: https://github.com/expo/expo/issues/27040

Currenty fails on this, need to fix an icon first : Error: [android.dangerous]: withAndroidDangerousBaseMod: ENOENT: no such file or directory, open './assets/adaptive-icon.png'
