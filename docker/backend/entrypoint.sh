#!/bin/bash

# Run Alembic upgrade to migrate the database
poetry run alembic upgrade head

# Start the Uvicorn server
exec poetry run uvicorn backend_api:app --host 0.0.0.0 --port 8000
