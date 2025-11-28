#!/bin/bash

# Startup script for Azure App Service
# This script initializes the database and starts the Flask application with Gunicorn

echo "Starting TaskForge API..."

# Set Python path
export PYTHONPATH=/home/site/wwwroot:$PYTHONPATH

# Create logs directory if it doesn't exist
mkdir -p /home/site/wwwroot/logs

# Initialize database (run migrations if needed)
echo "Initializing database..."
python -c "from app import create_app, db; app = create_app('production'); app.app_context().push(); db.create_all()" || echo "Database initialization failed or already initialized"

# Start Gunicorn with production settings
echo "Starting Gunicorn..."
gunicorn --bind=0.0.0.0:8000 \
         --workers=4 \
         --timeout=120 \
         --access-logfile /home/site/wwwroot/logs/access.log \
         --error-logfile /home/site/wwwroot/logs/error.log \
         --log-level info \
         "run:app"
