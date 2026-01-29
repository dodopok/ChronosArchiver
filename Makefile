# Makefile for ChronosArchiver

.PHONY: help start stop restart logs build test clean validate

help:
	@echo "ChronosArchiver - Available Commands:"
	@echo ""
	@echo "  make start       - Start all services"
	@echo "  make stop        - Stop all services"
	@echo "  make restart     - Restart all services"
	@echo "  make logs        - View logs (all services)"
	@echo "  make logs-api    - View API logs"
	@echo "  make logs-fe     - View frontend logs"
	@echo "  make build       - Build Docker images"
	@echo "  make rebuild     - Rebuild from scratch"
	@echo "  make test        - Run tests"
	@echo "  make validate    - Validate Docker setup"
	@echo "  make clean       - Clean up containers and volumes"
	@echo "  make status      - Show service status"
	@echo ""

start:
	@echo "Starting ChronosArchiver..."
	@bash scripts/start.sh

stop:
	@echo "Stopping ChronosArchiver..."
	@bash scripts/stop.sh

restart: stop start

logs:
	@docker-compose logs -f

logs-api:
	@docker-compose logs -f api

logs-fe:
	@docker-compose logs -f frontend

logs-worker:
	@docker-compose logs -f worker

build:
	@echo "Building Docker images..."
	@docker-compose build

rebuild:
	@bash scripts/rebuild.sh

test:
	@echo "Running backend tests..."
	@pytest tests/ -v
	@echo ""
	@echo "Running frontend tests..."
	@cd frontend && npm test

validate:
	@bash scripts/validate_docker.sh

status:
	@docker-compose ps

clean:
	@echo "Warning: This will remove all containers, volumes, and data"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	@docker-compose down -v
	@docker system prune -f
	@echo "✓ Cleanup complete"

scale-workers:
	@read -p "Enter number of workers: " count; \
	docker-compose up -d --scale worker=$$count

backup:
	@echo "Creating backup..."
	@tar -czf chronos-backup-$$(date +%Y%m%d-%H%M%S).tar.gz archive/ logs/ config.yaml
	@echo "✓ Backup created"

init:
	@echo "Initializing ChronosArchiver..."
	@mkdir -p archive logs
	@cp -n .env.example .env 2>/dev/null || true
	@cp -n config.yaml.example config.yaml 2>/dev/null || true
	@echo "✓ Initialization complete"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Edit .env with your configuration"
	@echo "  2. Edit config.yaml as needed"
	@echo "  3. Run 'make start' to start all services"
	@echo ""