# Docker Swarm Deployment Guide

## Quick Deployment

For routine updates (code changes, new features):

```bash
cd ~/sock-graveyard
./deploy-swarm.sh
```

## Manual Deployment Steps

If you need to deploy manually or troubleshoot:

### 1. Navigate to project directory
```bash
cd ~/sock-graveyard
```

### 2. Pull latest code
```bash
git pull
```

### 3. Build images (if code changed)
```bash
docker compose build --pull
```

### 4. Load environment variables
**CRITICAL:** Docker Swarm needs env vars exported for `${VARIABLE}` substitution
```bash
set -a
source .env
set +a
```

### 5. Deploy the stack
```bash
docker stack deploy -c docker-compose.yml sock-graveyard
```

### 6. Monitor deployment
```bash
# Check service status
docker service ls

# Watch backend logs
docker service logs sock-graveyard_backend --tail 50 -f

# Check specific service status
docker service ps sock-graveyard_backend --no-trunc
```

## First-Time Setup

### Initialize Swarm
```bash
docker swarm init
```

### Set PostgreSQL password in database
If you're migrating from an existing setup where postgres was initialized with default password:
```bash
# Get the correct password from .env
CORRECT_PASSWORD=$(grep POSTGRES_PASSWORD .env | head -1 | cut -d'=' -f2)

# Update postgres user password
docker exec $(docker ps -q -f name=sock-graveyard_postgres) \
  psql -U postgres -c "ALTER USER postgres WITH PASSWORD '$CORRECT_PASSWORD';"
```

### Deploy
```bash
cd ~/sock-graveyard
./deploy-swarm.sh
```

## Troubleshooting

### Services showing 0/2 replicas

1. Check service logs:
```bash
docker service logs sock-graveyard_backend --tail 50
```

2. Check task status:
```bash
docker service ps sock-graveyard_backend --no-trunc
```

3. Common issues:
   - **Password mismatch**: Ensure you ran `set -a; source .env; set +a` before deploying
   - **Network issues**: Check `docker network ls` and ensure `sock-graveyard_sock-network` exists
   - **Container crashes**: Check logs of failed containers with `docker logs <container-id>`

### Rollback deployment

If a deployment fails:
```bash
docker service update --rollback sock-graveyard_backend
docker service update --rollback sock-graveyard_frontend
docker service update --rollback sock-graveyard_nginx
```

### Clean restart

To completely restart the stack:
```bash
# Remove stack
docker stack rm sock-graveyard

# Wait for cleanup
sleep 30

# Verify services are gone
docker service ls

# Redeploy
set -a && source .env && set +a
docker stack deploy -c docker-compose.yml sock-graveyard
```

### Remove obsolete services

If you see old services (like `alembic-migration`):
```bash
docker service rm sock-graveyard_alembic-migration
```

## Monitoring

### Check service health
```bash
docker service ls
```

### View service logs
```bash
# All backend logs
docker service logs sock-graveyard_backend -f

# Last 100 lines
docker service logs sock-graveyard_backend --tail 100

# With timestamps
docker service logs sock-graveyard_backend --tail 50 -t

# Since last 5 minutes
docker service logs sock-graveyard_backend --since 5m
```

### Check running containers
```bash
docker ps | grep sock-graveyard
```

### Inspect service configuration
```bash
docker service inspect sock-graveyard_backend --pretty
```

## Important Notes

1. **Environment Variables**: Always run `set -a; source .env; set +a` before `docker stack deploy` to ensure proper variable substitution

2. **Rolling Updates**: The configuration uses `order: start-first` which means:
   - New containers start before old ones stop
   - Minimal downtime during updates
   - 2 replicas for backend and frontend ensure high availability

3. **Database Endpoint**: PostgreSQL uses `dnsrr` endpoint mode to avoid VIP routing issues in Swarm

4. **Build Time**: Building images takes ~10 minutes, but rolling updates ensure the site stays online

5. **Nginx**: Single replica is sufficient for the reverse proxy

6. **.env File**: Never commit `.env` to git - it contains secrets

## Site Access

After deployment, the site is available at:
- **Production**: http://socks.arnodece.com
- **Direct nginx**: http://<server-ip>:80

## Key Commands Reference

| Task | Command |
|------|---------|
| Deploy | `./deploy-swarm.sh` |
| Check status | `docker service ls` |
| View logs | `docker service logs sock-graveyard_backend -f` |
| Scale service | `docker service scale sock-graveyard_backend=3` |
| Update single service | `docker service update --force sock-graveyard_backend` |
| Rollback | `docker service update --rollback sock-graveyard_backend` |
| Remove stack | `docker stack rm sock-graveyard` |
| List networks | `docker network ls` |
| Inspect service | `docker service inspect sock-graveyard_backend` |
