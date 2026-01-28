# ChronosArchiver Usage Guide

Comprehensive guide for using ChronosArchiver in various scenarios.

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Basic Usage](#basic-usage)
- [Advanced Usage](#advanced-usage)
- [CLI Reference](#cli-reference)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

## Installation

### From PyPI

```bash
pip install chronos-archiver
```

### From Source

```bash
git clone https://github.com/dodopok/ChronosArchiver.git
cd ChronosArchiver
pip install -e .
```

### With Docker

```bash
docker pull chronosarchiver/chronos-archiver:latest
```

### Prerequisites

- Python 3.8 or higher
- Redis (for queue management)
- PostgreSQL (optional, for production)

## Quick Start

### 1. Initialize Project

```bash
chronos init
```

This creates:
- `archive/` directory for stored content
- `logs/` directory for log files
- `config.yaml` configuration file

### 2. Start Redis

```bash
# Using system Redis
redis-server

# Or with Docker
docker run -d -p 6379:6379 redis:7-alpine
```

### 3. Archive Your First URL

```bash
chronos archive https://web.archive.org/web/20090430060114/http://www.dar.org.br/
```

## Configuration

### Configuration File

Edit `config.yaml`:

```yaml
archive:
  output_dir: "./archive"
  user_agent: "ChronosArchiver/1.0"
  max_file_size: 100  # MB

queue:
  backend: "redis"
  redis_url: "redis://localhost:6379/0"

processing:
  workers: 4
  batch_size: 10
  retry_attempts: 3
  requests_per_second: 5

database:
  type: "sqlite"
  sqlite_path: "./archive/chronos.db"

transformation:
  rewrite_links: true
  extract_metadata: true
  remove_scripts: false
```

### Validate Configuration

```bash
chronos validate-config
```

## Basic Usage

### Archive a Single URL

```bash
chronos archive https://web.archive.org/web/20090430060114/http://www.dar.org.br/
```

### Archive Multiple URLs

```bash
# From file (one URL per line)
chronos archive --input urls.txt

# Multiple URLs as arguments
chronos archive URL1 URL2 URL3
```

### Archive with Custom Configuration

```bash
chronos archive --config custom_config.yaml --input urls.txt
```

### Specify Output Directory

```bash
chronos archive --output /path/to/archive URL
```

### Control Worker Count

```bash
chronos archive --workers 8 --input urls.txt
```

## Advanced Usage

### Background Workers

Start background workers for async processing:

```bash
# Start 4 workers
chronos workers start --count 4

# In another terminal, queue URLs
chronos archive --input urls.txt
```

### Programmatic Usage

#### Simple Example

```python
import asyncio
from chronos_archiver import ChronosArchiver
from chronos_archiver.config import load_config

async def main():
    config = load_config()
    archiver = ChronosArchiver(config)
    
    url = "https://web.archive.org/web/20090430060114/http://www.dar.org.br/"
    await archiver.archive_url(url)
    
    await archiver.shutdown()

asyncio.run(main())
```

#### Batch Processing

```python
import asyncio
from chronos_archiver import ChronosArchiver
from chronos_archiver.config import load_config

async def main():
    config = load_config()
    archiver = ChronosArchiver(config)
    
    urls = [
        "https://web.archive.org/web/20090430060114/http://www.dar.org.br/",
        "https://web.archive.org/web/20120302052501/http://www.dar.org.br/",
        "https://web.archive.org/web/20150406103050/http://dar.org.br/",
    ]
    
    await archiver.archive_urls(urls)
    await archiver.shutdown()

asyncio.run(main())
```

#### Custom Pipeline

```python
import asyncio
from chronos_archiver.discovery import WaybackDiscovery
from chronos_archiver.ingestion import ContentIngestion
from chronos_archiver.transformation import ContentTransformation
from chronos_archiver.indexing import ContentIndexer
from chronos_archiver.config import load_config

async def main():
    config = load_config()
    
    # Initialize components
    discovery = WaybackDiscovery(config)
    ingestion = ContentIngestion(config)
    transformation = ContentTransformation(config)
    indexer = ContentIndexer(config)
    
    # Stage 1: Discovery
    snapshots = await discovery.find_snapshots("http://www.dar.org.br/")
    print(f"Found {len(snapshots)} snapshots")
    
    for snapshot in snapshots[:5]:  # Process first 5
        # Stage 2: Ingestion
        content = await ingestion.download(snapshot)
        if not content:
            continue
        
        # Stage 3: Transformation
        transformed = await transformation.transform(content)
        if not transformed:
            continue
        
        # Stage 4: Indexing
        indexed = await indexer.index(transformed)
        if indexed:
            print(f"Archived: {transformed.metadata.get('title')}")
    
    await indexer.close()

asyncio.run(main())
```

### Search Archived Content

```python
import asyncio
from chronos_archiver.indexing import ContentIndexer
from chronos_archiver.config import load_config

async def search():
    config = load_config()
    indexer = ContentIndexer(config)
    
    results = await indexer.search("Diocese Anglicana", limit=10)
    
    for result in results:
        print(f"Title: {result.metadata.get('title')}")
        if result.text_content:
            print(f"Preview: {result.text_content[:100]}...\n")
    
    await indexer.close()

asyncio.run(search())
```

### Discover All Snapshots

```python
import asyncio
from chronos_archiver.discovery import WaybackDiscovery
from chronos_archiver.config import load_config

async def discover():
    config = load_config()
    discovery = WaybackDiscovery(config)
    
    # Find all snapshots for a URL
    snapshots = await discovery.find_snapshots("http://www.dar.org.br/")
    
    print(f"Found {len(snapshots)} snapshots:\n")
    for snapshot in snapshots:
        print(f"{snapshot.timestamp}: {snapshot.status_code} - {snapshot.mime_type}")

asyncio.run(discover())
```

## CLI Reference

### `chronos archive`

Archive URLs from the Wayback Machine.

**Usage**:
```bash
chronos archive [OPTIONS] [URLS]...
```

**Options**:
- `--input, -i PATH`: File with URLs (one per line)
- `--config, -c PATH`: Configuration file
- `--workers, -w INT`: Number of workers (default: 4)
- `--output, -o PATH`: Output directory

**Examples**:
```bash
chronos archive URL
chronos archive --input urls.txt --workers 8
chronos archive --config custom.yaml URL1 URL2
```

### `chronos workers`

Manage background workers.

#### `chronos workers start`

Start background workers.

**Usage**:
```bash
chronos workers start [OPTIONS]
```

**Options**:
- `--count, -c INT`: Number of workers (default: 4)
- `--config PATH`: Configuration file

**Example**:
```bash
chronos workers start --count 8
```

### `chronos init`

Initialize a new ChronosArchiver project.

**Usage**:
```bash
chronos init [OPTIONS]
```

**Options**:
- `--config, -c PATH`: Custom config file path

**Example**:
```bash
chronos init --config my_config.yaml
```

### `chronos validate-config`

Validate configuration file.

**Usage**:
```bash
chronos validate-config [OPTIONS]
```

**Options**:
- `--config, -c PATH`: Configuration file to validate

**Example**:
```bash
chronos validate-config --config config.yaml
```

## Troubleshooting

### Redis Connection Error

**Problem**: `Connection refused` when connecting to Redis

**Solution**:
```bash
# Check if Redis is running
redis-cli ping
# Should return: PONG

# If not running, start Redis
redis-server

# Or with Docker
docker run -d -p 6379:6379 redis:7-alpine
```

### Rate Limiting

**Problem**: Getting rate limited by Wayback Machine

**Solution**: Adjust rate limiting in `config.yaml`:
```yaml
processing:
  requests_per_second: 2  # Lower value
  retry_delay: 10  # Increase delay
```

### Memory Issues

**Problem**: Out of memory errors

**Solution**:
1. Reduce concurrent requests:
   ```yaml
   processing:
     concurrent_requests: 5
   ```

2. Reduce batch size:
   ```yaml
   processing:
     batch_size: 5
   ```

3. Enable compression:
   ```yaml
   indexing:
     compress_content: true
   ```

### Database Locked

**Problem**: `database is locked` error with SQLite

**Solution**: Use PostgreSQL for concurrent access:
```yaml
database:
  type: "postgresql"
  postgresql_url: "postgresql://user:pass@localhost:5432/chronos"
```

### Import Errors

**Problem**: `ModuleNotFoundError`

**Solution**:
```bash
# Reinstall ChronosArchiver
pip install --force-reinstall -e .

# Or install from PyPI
pip install --upgrade chronos-archiver
```

## Best Practices

### 1. Start Small

Test with a few URLs before large-scale archiving:
```bash
chronos archive --input test_urls.txt
```

### 2. Use Background Workers

For large batches, use background workers:
```bash
# Terminal 1: Start workers
chronos workers start --count 8

# Terminal 2: Queue URLs
chronos archive --input large_list.txt
```

### 3. Monitor Progress

Check logs:
```bash
tail -f logs/chronos.log
```

### 4. Regular Backups

Backup your archive and database:
```bash
tar -czf archive_backup.tar.gz archive/
```

### 5. Optimize Configuration

For fast networks:
```yaml
processing:
  workers: 8
  concurrent_requests: 20
  requests_per_second: 10
```

For slow networks:
```yaml
processing:
  workers: 2
  concurrent_requests: 5
  requests_per_second: 2
```

### 6. Use PostgreSQL in Production

```yaml
database:
  type: "postgresql"
  postgresql_url: "postgresql://user:pass@host:5432/chronos"
  pool_size: 10
```

### 7. Enable Compression

Save disk space:
```yaml
indexing:
  compress_content: true
  compression_level: 6
```

### 8. Respect Rate Limits

Avoid overwhelming the Wayback Machine:
```yaml
processing:
  requests_per_second: 5  # Conservative
  retry_delay: 5
```

### 9. Filter Content

Only archive what you need:
```yaml
archive:
  allowed_mime_types:
    - "text/html"
    - "text/css"
    - "application/javascript"

discovery:
  filter_status_codes: [200]
```

### 10. Regular Maintenance

Clean up failed entries, optimize database, check disk space.

## Docker Usage

### Using Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f chronos

# Scale workers
docker-compose up -d --scale chronos-worker=4

# Stop services
docker-compose down
```

### Custom Docker Run

```bash
docker run -d \
  --name chronos-redis \
  -p 6379:6379 \
  redis:7-alpine

docker run -d \
  --name chronos-archiver \
  --link chronos-redis:redis \
  -v $(pwd)/archive:/app/archive \
  -v $(pwd)/config.yaml:/app/config.yaml:ro \
  -e REDIS_URL=redis://redis:6379/0 \
  chronosarchiver/chronos-archiver:latest \
  chronos workers start --count 4
```

## Performance Tips

### 1. Concurrent Processing

Use `asyncio.gather()` for parallel operations:
```python
await asyncio.gather(*[process(url) for url in urls])
```

### 2. Connection Pooling

Reuse HTTP connections:
```python
async with aiohttp.ClientSession() as session:
    # All requests reuse connections
```

### 3. Batch Operations

Process in batches:
```python
for batch in chunks(items, batch_size=10):
    await process_batch(batch)
```

### 4. Index Optimization

For PostgreSQL, create indexes:
```sql
CREATE INDEX idx_url ON archived_pages(url);
CREATE INDEX idx_timestamp ON archived_pages(timestamp);
```

### 5. Resource Monitoring

Monitor system resources:
```bash
# CPU and memory
htop

# Disk I/O
iotop

# Network
iftop
```