#!/bin/bash

set -e

echo "Waiting for database to be ready..."
echo "DB Config: host=postgres, user=$POSTGRES_USER, db=$POSTGRES_DB"

# Wait for PostgreSQL to be ready
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "postgres" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q' 2>&1; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done

echo "PostgreSQL is up - running migrations"

# Run database migrations
alembic upgrade head

echo "Migrations complete - starting application"

# Start the application
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
