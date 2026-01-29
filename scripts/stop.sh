#!/bin/bash
# Stop script for ChronosArchiver

echo "Stopping ChronosArchiver services..."

docker-compose down

echo ""
echo "✓ All services stopped"
echo ""
echo "To remove volumes (data will be lost), run:"
echo "  docker-compose down -v"
echo ""