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

echo "⏳ Waiting for services to stabilize..."
sleep 45

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
