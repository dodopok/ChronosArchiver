#!/bin/bash
# Startup script for ChronosArchiver

set -e

echo "========================================"
echo "Starting ChronosArchiver"
echo "========================================"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running"
    echo "Please start Docker and try again"
    exit 1
fi

# Create necessary directories
echo "Creating directories..."
mkdir -p archive logs

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from example..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration"
fi

# Copy config if it doesn't exist
if [ ! -f config.yaml ]; then
    echo "Creating config.yaml from example..."
    cp config.yaml.example config.yaml
fi

# Pull latest images
echo ""
echo "Pulling Docker images..."
docker-compose pull

# Build custom images
echo ""
echo "Building custom images..."
docker-compose build

# Start services
echo ""
echo "Starting services..."
docker-compose up -d

# Wait for services to be healthy
echo ""
echo "Waiting for services to be healthy..."
echo "This may take 30-60 seconds..."
echo ""

sleep 10

# Check service status
for i in {1..12}; do
    healthy=$(docker-compose ps | grep -c "(healthy)" || true)
    total=$(docker-compose ps --services | wc -l)
    
    echo "Services healthy: $healthy/$total"
    
    if [ "$healthy" -eq "$total" ] || [ $i -eq 12 ]; then
        break
    fi
    
    sleep 5
done

echo ""
echo "========================================"
echo "ChronosArchiver Started!"
echo "========================================"
echo ""
echo "Services:"
echo "  🌐 Frontend:  http://localhost:3000"
echo "  🔧 API:       http://localhost:8000"
echo "  📚 API Docs:  http://localhost:8000/api/docs"
echo "  🔍 Meilisearch: http://localhost:7700"
echo ""
echo "Commands:"
echo "  View logs:    docker-compose logs -f"
echo "  Stop:         docker-compose down"
echo "  Restart:      docker-compose restart"
echo ""
echo "To validate setup, run:"
echo "  bash scripts/validate_docker.sh"
echo ""