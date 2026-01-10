#!/bin/bash

set -e

echo "🚀 Starting deployment with rolling updates..."

echo "📥 Pulling latest code..."
git pull

echo "🔨 Building and tagging images..."
docker compose build --pull

echo "🔄 Deploying with rolling update..."
docker stack deploy -c docker-compose.yml sock-graveyard

echo "⏳ Waiting for services to stabilize..."
sleep 30

echo "📊 Service status:"
docker service ls

echo ""
echo "🔍 Backend service details:"
docker service ps sock-graveyard_backend --no-trunc

echo ""
echo "🔍 Frontend service details:"
docker service ps sock-graveyard_frontend --no-trunc

echo ""
echo "✅ Deployment complete!"
