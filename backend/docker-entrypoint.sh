#!/bin/bash

set -e

echo "================================================"
echo "🚀 Starting Barangay Kiosk Backend"
echo "================================================"

# Function to wait for database
wait_for_db() {
    echo "⏳ Waiting for database to be ready..."
    MAX_RETRIES=30
    RETRY_COUNT=0
    
    while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
        if python -c "
import psycopg2
import os
from urllib.parse import urlparse

db_url = os.getenv('DATABASE_URL')
parsed = urlparse(db_url)

try:
    conn = psycopg2.connect(
        host=parsed.hostname,
        port=parsed.port,
        user=parsed.username,
        password=parsed.password,
        database=parsed.path[1:]
    )
    conn.close()
    print('✅ Database is ready!')
    exit(0)
except Exception as e:
    print(f'❌ Database not ready: {e}')
    exit(1)
" 2>/dev/null; then
            echo "✅ Database connection successful!"
            return 0
        fi
        
        RETRY_COUNT=$((RETRY_COUNT + 1))
        echo "⏳ Attempt $RETRY_COUNT/$MAX_RETRIES - Retrying in 2 seconds..."
        sleep 2
    done
    
    echo "❌ Failed to connect to database after $MAX_RETRIES attempts"
    exit 1
}

# Function to run migrations
run_migrations() {
    echo ""
    echo "================================================"
    echo "📦 Running Database Migrations"
    echo "================================================"
    
    if alembic upgrade head; then
        echo "✅ Migrations completed successfully!"
    else
        echo "❌ Migration failed!"
        exit 1
    fi
}

# Function to seed database
seed_database() {
    echo ""
    echo "================================================"
    echo "🌱 Seeding Database"
    echo "================================================"
    
    if python -c "
import sys
sys.path.insert(0, '/app')

from seeds.run_all import seed_all

try:
    seed_all()
    print('✅ Database seeding completed!')
except Exception as e:
    print(f'⚠️  Seeding warning: {e}')
    print('This is normal if data already exists.')
"; then
        echo "✅ Database seeding process completed!"
    else
        echo "⚠️  Seeding had issues but continuing..."
    fi
}

# Function to start server
start_server() {
    echo ""
    echo "================================================"
    echo "🌐 Starting FastAPI Server"
    echo "================================================"
    echo "Server will be available at http://0.0.0.0:8000"
    echo "Docs will be available at http://0.0.0.0:8000/docs"
    echo "================================================"
    echo ""
    
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
}

# Main execution
wait_for_db
run_migrations
seed_database
start_server