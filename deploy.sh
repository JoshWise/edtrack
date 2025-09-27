#!/bin/bash

# EdTrack Deployment Script
set -e

echo "🚀 EdTrack Deployment Script"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Parse command line arguments
ENV=${1:-prod}
DB_PASSWORD=${2:-$(openssl rand -base64 32)}

echo "📦 Environment: $ENV"
echo "🔐 Database password: $DB_PASSWORD"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
POSTGRES_USER=postgres
POSTGRES_PASSWORD=$DB_PASSWORD
POSTGRES_DB=edtrack
EOF
    echo "✅ .env file created with secure password"
fi

# Build and start services
echo "🔨 Building and starting services..."
docker-compose -f docker-compose.prod.yml --env-file .env up -d --build

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 10

# Initialize database
echo "🗄️ Initializing database..."
docker-compose -f docker-compose.prod.yml exec app python init_db.py

echo "✅ Deployment complete!"
echo "🌐 Application available at: http://localhost:8501"
echo "📊 Database connection: postgresql://postgres:$DB_PASSWORD@localhost:5432/edtrack"
echo ""
echo "📋 Useful commands:"
echo "  View logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "  Stop: docker-compose -f docker-compose.prod.yml down"
echo "  Restart: docker-compose -f docker-compose.prod.yml restart"
