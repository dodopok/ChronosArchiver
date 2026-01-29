#!/bin/bash
# Validation script for ChronosArchiver Docker setup

set -e

echo "========================================"
echo "ChronosArchiver Docker Validation"
echo "========================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_service() {
    local service=$1
    local url=$2
    local expected=$3
    
    echo -n "Checking $service... "
    
    if curl -f -s "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC}"
        return 0
    else
        echo -e "${RED}✗${NC}"
        return 1
    fi
}

check_container() {
    local container=$1
    
    echo -n "Checking container $container... "
    
    if docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
        local health=$(docker inspect --format='{{.State.Health.Status}}' $container 2>/dev/null || echo "no-healthcheck")
        
        if [ "$health" = "healthy" ] || [ "$health" = "no-healthcheck" ]; then
            echo -e "${GREEN}✓${NC} ($health)"
            return 0
        else
            echo -e "${YELLOW}⚠${NC} ($health)"
            return 1
        fi
    else
        echo -e "${RED}✗${NC} (not running)"
        return 1
    fi
}

echo "1. Checking Docker containers..."
echo ""

check_container "chronos-redis"
check_container "chronos-meilisearch"
check_container "chronos-tika"
check_container "chronos-postgres"
check_container "chronos-api"
check_container "chronos-frontend"

echo ""
echo "2. Checking service endpoints..."
echo ""

check_service "Frontend" "http://localhost:3000" "200"
check_service "API" "http://localhost:8000/health" "200"
check_service "API Docs" "http://localhost:8000/api/docs" "200"
check_service "Meilisearch" "http://localhost:7700/health" "200"
check_service "Tika" "http://localhost:9998/tika" "200"

echo ""
echo "3. Testing API endpoints..."
echo ""

echo -n "Testing search API... "
if curl -f -s "http://localhost:8000/api/search?q=test" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
fi

echo -n "Testing suggestions API... "
if curl -f -s "http://localhost:8000/api/suggest?q=test" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
fi

echo -n "Testing stats API... "
if curl -f -s "http://localhost:8000/api/stats" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
fi

echo ""
echo "4. Checking volumes..."
echo ""

if [ -d "./archive" ]; then
    echo -e "Archive directory: ${GREEN}✓${NC}"
else
    echo -e "Archive directory: ${RED}✗${NC}"
fi

if [ -d "./logs" ]; then
    echo -e "Logs directory: ${GREEN}✓${NC}"
else
    echo -e "Logs directory: ${RED}✗${NC}"
fi

echo ""
echo "5. Checking network..."
echo ""

if docker network ls | grep -q chronos-network; then
    echo -e "Docker network: ${GREEN}✓${NC}"
else
    echo -e "Docker network: ${RED}✗${NC}"
fi

echo ""
echo "========================================"
echo "Validation Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "  - Access frontend: http://localhost:3000"
echo "  - Access API docs: http://localhost:8000/api/docs"
echo "  - View logs: docker-compose logs -f"
echo ""