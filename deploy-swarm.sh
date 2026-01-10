#!/bin/bash

set -e

echo "🚀 Starting high-availability deployment with Docker Swarm..."

echo "📥 Pulling latest code..."
git pull

echo "🔨 Building new images..."
docker compose build --pull

# Docker swarm env_file doesn't work: https://blog.justanotheruptime.com/posts/2025_09_25_env_file_and_docker_swarm/
echo "� Loading environment variables from .env..."
set -a
source .env
set +a
echo "✓ Environment variables loaded"

echo "�🔄 Deploying stack with rolling updates..."
docker stack deploy -c docker-compose.yml sock-graveyard

echo "⏳ Waiting for backend containers to be ready..."
sleep 15

echo "🗃️ Running database migrations..."
BACKEND_CONTAINER=$(docker ps -q -f "label=com.docker.swarm.service.name=sock-graveyard_backend" | head -n 1)
if [ -n "$BACKEND_CONTAINER" ]; then
  echo "Waiting for database to be ready..."
  until docker exec $BACKEND_CONTAINER sh -c "PGPASSWORD=\$POSTGRES_PASSWORD psql -h postgres -U \$POSTGRES_USER -d \$POSTGRES_DB -c '\q'" 2>&1 > /dev/null; do
    echo "PostgreSQL is unavailable - sleeping"
    sleep 2
  done
  echo "✓ Database is ready"
  
  docker exec $BACKEND_CONTAINER alembic upgrade head
  echo "✓ Migrations complete"
else
  echo "⚠️ No backend container found - skipping migrations"
fi

echo "⏳ Waiting for services to stabilize..."
sleep 15

echo "📊 Service status:"
docker service ls

echo ""
echo "🔍 Detailed status:"
docker service ps sock-graveyard_backend --no-trunc | head -5
docker service ps sock-graveyard_frontend --no-trunc | head -5
docker service ps sock-graveyard_nginx --no-trunc | head -3

echo ""
echo "✅ Deployment complete!"
echo "Site available at: http://socks.arnodece.com"
