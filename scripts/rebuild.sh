#!/bin/bash
# Rebuild and restart ChronosArchiver

echo "Rebuilding ChronosArchiver..."
echo ""

# Stop services
echo "Stopping services..."
docker-compose down

# Rebuild
echo ""
echo "Rebuilding images..."
docker-compose build --no-cache

# Start
echo ""
echo "Starting services..."
docker-compose up -d

echo ""
echo "Waiting for services to be healthy..."
sleep 20

# Show status
echo ""
docker-compose ps

echo ""
echo "✓ Rebuild complete!"
echo ""
echo "Access:"
echo "  Frontend: http://localhost:3000"
echo "  API:      http://localhost:8000"
echo ""