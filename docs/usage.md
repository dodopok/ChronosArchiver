# ChronosArchiver Usage Guide

Comprehensive guide for using ChronosArchiver.

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [CLI Usage](#cli-usage)
4. [Programmatic Usage](#programmatic-usage)
5. [Configuration](#configuration)
6. [Common Workflows](#common-workflows)
7. [Troubleshooting](#troubleshooting)

## Installation

### Prerequisites

- Python 3.8+
- Redis (for queue management)
- SQLite or PostgreSQL

### Install from PyPI

```bash
pip install chronos-archiver
```

### Install from Source

```bash
git clone https://github.com/dodopok/ChronosArchiver.git
cd ChronosArchiver
pip install -e .
```

### Development Installation

```bash
pip install -e ".[dev]"
```

## Quick Start

### 1. Initialize Project

```bash
chronos init
```

This creates:
- `archive/` directory
- `logs/` directory  
- `config.yaml` configuration file

### 2. Start Redis

```bash
redis-server
```

### 3. Archive a URL

```bash
chronos archive https://web.archive.org/web/20090430060114/http://www.dar.org.br/
```

## CLI Usage

### Archive Commands

#### Archive Single URL

```bash
chronos archive <url>
```

#### Archive Multiple URLs

```bash
chronos archive <url1> <url2> <url3>
```

#### Archive from File

```bash
chronos archive --input urls.txt
```

#### Custom Configuration

```bash
chronos archive --config custom.yaml --input urls.txt
```

#### Set Worker Count

```bash
chronos archive --workers 8 --input urls.txt
```

#### Custom Output Directory

```bash
chronos archive --output /path/to/archive <url>
```

### Worker Management

#### Start Workers

```bash
chronos workers start --count 4
```

#### Start with Custom Config

```bash
chronos workers start --config custom.yaml --count 8
```

### Validation

#### Validate Configuration

```bash
chronos validate-config
chronos validate-config --config custom.yaml
```

### Help

```bash
chronos --help
chronos archive --help
chronos workers --help
```

## Programmatic Usage

### Basic Example

```python
import asyncio
from chronos_archiver import ChronosArchiver
from chronos_archiver.config import load_config

async def main():
    config = load_config()
    archiver = ChronosArchiver(config)
    
    await archiver.archive_url(
        'https://web.archive.org/web/20090430060114/http://www.dar.org.br/'
    )
    
    await archiver.shutdown()

asyncio.run(main())
```

### Multiple URLs

```python
urls = [
    'https://web.archive.org/web/20090430060114/http://www.dar.org.br/',
    'https://web.archive.org/web/20120302052501/http://www.dar.org.br/',
]

await archiver.archive_urls(urls)
```

### Manual Pipeline

```python
from chronos_archiver.discovery import WaybackDiscovery
from chronos_archiver.ingestion import ContentIngestion
from chronos_archiver.transformation import ContentTransformation
from chronos_archiver.indexing import ContentIndexer

# Initialize modules
discovery = WaybackDiscovery(config)
ingestion = ContentIngestion(config)
transformation = ContentTransformation(config)
indexer = ContentIndexer(config)

# Stage 1: Discovery
snapshots = await discovery.find_snapshots(url)

# Stage 2: Ingestion
for snapshot in snapshots:
    downloaded = await ingestion.download(snapshot)
    
    # Stage 3: Transformation
    if downloaded:
        transformed = await transformation.transform(downloaded)
        
        # Stage 4: Indexing
        if transformed:
            await indexer.index(transformed)
```

### Search Archived Content

```python
from chronos_archiver.indexing import ContentIndexer

indexer = ContentIndexer(config)
results = await indexer.search("Diocese Anglicana", limit=10)

for result in results:
    print(f"Title: {result.metadata.get('title')}")
    print(f"Text: {result.text_content[:200]}...")
```

## Configuration

### Configuration File Structure

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
```

### Load Configuration

```python
from chronos_archiver.config import load_config, save_config

# Load
config = load_config('config.yaml')

# Modify
config['processing']['workers'] = 8

# Save
save_config(config, 'new_config.yaml')
```

## Common Workflows

### Workflow 1: Archive Historical Snapshots

```python
# Discover all snapshots of a URL
from chronos_archiver.discovery import WaybackDiscovery

discovery = WaybackDiscovery(config)
snapshots = await discovery.find_snapshots('http://www.dar.org.br/')

print(f"Found {len(snapshots)} snapshots")

# Archive all snapshots
for snapshot in snapshots:
    await archiver.archive_url(snapshot.url)
```

### Workflow 2: Batch Processing

```python
# Read URLs from file
with open('urls.txt') as f:
    urls = [line.strip() for line in f if line.strip()]

# Process in batches
batch_size = 10
for i in range(0, len(urls), batch_size):
    batch = urls[i:i+batch_size]
    await archiver.archive_urls(batch)
    print(f"Processed {i+len(batch)}/{len(urls)}")
```

### Workflow 3: Monitor Progress

```python
from chronos_archiver.models import ProcessingStats
from tqdm import tqdm

stats = ProcessingStats(total_snapshots=len(urls))

for url in tqdm(urls, desc="Archiving"):
    try:
        await archiver.archive_url(url)
        stats.indexed += 1
    except Exception as e:
        stats.failed += 1
        print(f"Failed: {url} - {e}")

print(f"Success rate: {stats.success_rate:.1f}%")
```

### Workflow 4: Custom Processing

```python
# Custom content filter
async def should_archive(snapshot):
    """Only archive HTML pages from specific year."""
    if snapshot.mime_type != 'text/html':
        return False
    if not snapshot.timestamp.startswith('2009'):
        return False
    return True

# Apply filter
snapshots = await discovery.find_snapshots(url)
filtered = [s for s in snapshots if await should_archive(s)]

for snapshot in filtered:
    await archiver.archive_url(snapshot.url)
```

## Troubleshooting

### Connection Errors

**Problem**: `ConnectionError: Cannot connect to Redis`

**Solution**:
```bash
# Start Redis
redis-server

# Or use in-memory queuing (for testing)
# Set in config.yaml:
queue:
  backend: "memory"
```

### Download Failures

**Problem**: `Download failed: timeout`

**Solution**:
```yaml
# Increase timeout in config.yaml
processing:
  download_timeout: 600  # 10 minutes
```

### Rate Limiting

**Problem**: Too many requests blocked

**Solution**:
```yaml
# Reduce request rate
processing:
  requests_per_second: 2
  concurrent_requests: 5
```

### Memory Issues

**Problem**: Out of memory errors

**Solution**:
```yaml
# Reduce file size limit
archive:
  max_file_size: 50  # MB

# Reduce concurrency
processing:
  workers: 2
  batch_size: 5
```

### Database Locked

**Problem**: `database is locked` (SQLite)

**Solution**:
```yaml
# Use PostgreSQL for production
database:
  type: "postgresql"
  postgresql_url: "postgresql://user:pass@localhost/chronos"
```

### Debug Mode

```yaml
logging:
  level: "DEBUG"
  log_to_file: true
  log_file: "./logs/debug.log"
```

```python
# In code
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

**Need help?** Open an issue on [GitHub](https://github.com/dodopok/ChronosArchiver/issues)

**Last Updated**: January 2026  
**Version**: 1.0.0