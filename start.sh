#!/bin/bash
set -e

echo "Starting Vehicle Management System..."

# Wait for database to be ready (if using PostgreSQL)
if [[ $DATABASE_URL == postgres* ]]; then
    echo "Waiting for PostgreSQL to be ready..."
    until pg_isready -h $(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\).*/\1/p') -p 5432; do
        echo "PostgreSQL is unavailable - sleeping"
        sleep 2
    done
    echo "PostgreSQL is ready!"
fi

# Run database migrations (create tables if they don't exist)
echo "Initializing database..."
python3 -c "from app.database import init_db; init_db()"

# Start the application
echo "Starting web server..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
