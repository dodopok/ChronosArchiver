# 🐳 Docker Setup Guide for ChronosArchiver

## 🚀 Quick Start

```bash
# 1. Clone repository
git clone https://github.com/dodopok/ChronosArchiver.git
cd ChronosArchiver

# 2. Copy environment file
cp .env.example .env

# 3. (Optional) Edit configuration
nano .env

# 4. Start all services
docker-compose up -d

# 5. Check service status
docker-compose ps

# 6. View logs
docker-compose logs -f
```

---

## 📊 Service Architecture

### All Services (8)

| Service | Port | Purpose | Status |
|---------|------|---------|--------|
| **frontend** | 3000 | React web interface | ✅ |
| **api** | 8000 | FastAPI backend + WebSocket | ✅ |
| **redis** | 6379 | Message queues | ✅ |
| **meilisearch** | 7700 | Search engine | ✅ |
| **tika** | 9998 | Text extraction | ✅ |
| **postgres** | 5432 | Database | ✅ |
| **worker** | - | Background processing (x2) | ✅ |

---

## 🔧 Service Dependencies

```
frontend
  └─> api
       ├─> redis
       ├─> meilisearch
       └─> tika

worker
  ├─> redis
  ├─> meilisearch  
  ├─> tika
  └─> postgres
```

---

## ✅ Health Checks

All services have health checks configured:

```bash
# Check all services
docker-compose ps

# Should show all as "healthy"
```

### Individual Health Checks

```bash
# Redis
redis-cli -h localhost ping
# Should return: PONG

# Meilisearch
curl http://localhost:7700/health
# Should return: {"status":"available"}

# Tika
curl http://localhost:9998/tika
# Should return: Apache Tika version info

# PostgreSQL
psql -h localhost -U chronos -d chronos -c "SELECT 1;"
# Should return: 1

# API
curl http://localhost:8000/health
# Should return: {"status":"healthy",...}

# Frontend
curl http://localhost:3000
# Should return: HTML page
```

---

## 📦 Volume Management

### Volumes Created

```bash
docker volume ls | grep chronos
```

You should see:
- `chronosarchiver_redis-data`
- `chronosarchiver_meilisearch-data`
- `chronosarchiver_postgres-data`

### Backup Volumes

```bash
# Backup Redis
docker run --rm \
  -v chronosarchiver_redis-data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/redis-backup.tar.gz /data

# Backup Meilisearch
docker run --rm \
  -v chronosarchiver_meilisearch-data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/meilisearch-backup.tar.gz /data

# Backup PostgreSQL
docker-compose exec postgres pg_dump -U chronos chronos > postgres-backup.sql
```

---

## 🔄 Common Commands

### Start/Stop Services

```bash
# Start all
docker-compose up -d

# Stop all
docker-compose down

# Stop and remove volumes (CAUTION: deletes data)
docker-compose down -v

# Restart specific service
docker-compose restart api
docker-compose restart frontend
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f frontend
docker-compose logs -f worker

# Last 100 lines
docker-compose logs --tail=100 api
```

### Scale Workers

```bash
# Scale to 4 workers
docker-compose up -d --scale worker=4

# Scale to 1 worker
docker-compose up -d --scale worker=1
```

### Rebuild Services

```bash
# Rebuild all
docker-compose build

# Rebuild specific service
docker-compose build api
docker-compose build frontend

# Rebuild without cache
docker-compose build --no-cache

# Rebuild and restart
docker-compose up -d --build
```

---

## 🐞 Troubleshooting

### Issue: Services not starting

```bash
# Check Docker daemon
sudo systemctl status docker

# Check disk space
df -h

# Check Docker logs
sudo journalctl -u docker -f
```

### Issue: Port already in use

```bash
# Find what's using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or change port in docker-compose.yml
```

### Issue: Frontend can't connect to API

```bash
# Check API is running
curl http://localhost:8000/health

# Check frontend environment
docker-compose exec frontend cat /etc/nginx/conf.d/default.conf

# Check network
docker network inspect chronosarchiver_chronos-network
```

### Issue: Container fails health check

```bash
# View container logs
docker-compose logs <service-name>

# Check container status
docker-compose ps

# Inspect container
docker inspect chronos-<service-name>

# Access container shell
docker-compose exec <service-name> sh
```

### Issue: Database connection errors

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check credentials in .env
cat .env | grep POSTGRES

# Test connection
docker-compose exec postgres psql -U chronos -d chronos -c "SELECT 1;"
```

### Issue: Meilisearch not indexing

```bash
# Check Meilisearch is accessible
curl http://localhost:7700/health

# Check indexes
curl http://localhost:7700/indexes

# View Meilisearch logs
docker-compose logs meilisearch
```

### Issue: Tika not extracting

```bash
# Check Tika is running
curl http://localhost:9998/tika

# Test extraction
echo "Test content" | curl -X PUT http://localhost:9998/tika --data-binary @-

# View Tika logs
docker-compose logs tika
```

---

## 📊 Monitoring

### Resource Usage

```bash
# View resource usage
docker stats

# Specific container
docker stats chronos-api
```

### Container Health

```bash
# Check health status
docker-compose ps

# Inspect health
docker inspect --format='{{.State.Health.Status}}' chronos-api
```

---

## 🧹 Cleanup

### Remove Everything

```bash
# Stop and remove containers
docker-compose down

# Remove volumes (CAUTION: deletes all data)
docker-compose down -v

# Remove images
docker-compose down --rmi all

# Complete cleanup
docker system prune -a --volumes
```

### Clean Rebuild

```bash
# Stop everything
docker-compose down -v

# Remove old images
docker-compose rm -f

# Rebuild from scratch
docker-compose build --no-cache

# Start fresh
docker-compose up -d
```

---

## 🔐 Production Configuration

### Environment Variables for Production

Create `.env` file:

```env
# Strong passwords
POSTGRES_PASSWORD=your_very_secure_password_here
MEILI_MASTER_KEY=your_secure_meilisearch_master_key

# Use PostgreSQL in production
DATABASE_TYPE=postgresql

# Production API URL
VITE_API_URL=https://api.yourdomain.com
VITE_WS_URL=wss://api.yourdomain.com
```

### Production docker-compose.override.yml

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  api:
    command: uvicorn chronos_archiver.api:app --host 0.0.0.0 --port 8000 --workers 4
    environment:
      - DATABASE_TYPE=postgresql
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G

  worker:
    deploy:
      replicas: 4
      resources:
        limits:
          cpus: '1'
          memory: 2G

  postgres:
    environment:
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - /var/lib/postgresql/data:/var/lib/postgresql/data
```

Run with:
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## ✅ Verification Checklist

### After `docker-compose up -d`:

- [ ] All 8 services show as "Up"
- [ ] All services show as "healthy"
- [ ] Frontend accessible at http://localhost:3000
- [ ] API accessible at http://localhost:8000
- [ ] API docs at http://localhost:8000/api/docs
- [ ] Meilisearch at http://localhost:7700
- [ ] No errors in logs
- [ ] WebSocket connects (check browser console)
- [ ] Can archive a test URL
- [ ] Search returns results

---

**🎉 Docker Setup Complete! 🎉**