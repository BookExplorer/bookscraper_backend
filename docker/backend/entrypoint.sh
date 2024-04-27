#!/bin/bash

# Wait for the PostgreSQL database to be ready
echo "Waiting for PostgreSQL to start..."
while ! nc -z db 5432; do
  sleep 1
done
echo "PostgreSQL is up - executing command"

# Run Alembic migrations
echo "Running Alembic upgrade"
poetry run alembic upgrade head

# Start the Uvicorn server
echo "Starting Uvicorn server"
exec poetry run uvicorn backend_api:app --host 0.0.0.0 --port 8000
