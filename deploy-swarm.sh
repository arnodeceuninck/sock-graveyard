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

echo "⏳ Waiting for postgres to be ready..."
sleep 10

echo "🗃️ Running database migrations..."
docker run --rm \
  --network sock-network \
  -v "$(pwd)/backend/alembic:/app/alembic:ro" \
  -v "$(pwd)/backend/alembic.ini:/app/alembic.ini:ro" \
  -v "$(pwd)/backend/app:/app/app:ro" \
  -e DATABASE_URL="postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}" \
  -e POSTGRES_USER="${POSTGRES_USER}" \
  -e POSTGRES_PASSWORD="${POSTGRES_PASSWORD}" \
  -e POSTGRES_DB="${POSTGRES_DB}" \
  sock-graveyard-backend:latest \
  sh -c "
    echo 'Waiting for database...';
    until PGPASSWORD=\$POSTGRES_PASSWORD psql -h postgres -U \$POSTGRES_USER -d \$POSTGRES_DB -c '\q' 2>&1; do
      echo 'PostgreSQL is unavailable - sleeping';
      sleep 2;
    done;
    echo 'Running migrations...';
    alembic upgrade head;
    echo 'Migrations complete!';
  "

echo "⏳ Waiting for services to stabilize..."
sleep 30

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
