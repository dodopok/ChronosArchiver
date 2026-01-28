# ChronosArchiver API Reference

Complete API documentation for all modules and classes.

## Table of Contents

1. [Core API](#core-api)
2. [Discovery Module](#discovery-module)
3. [Ingestion Module](#ingestion-module)
4. [Transformation Module](#transformation-module)
5. [Indexing Module](#indexing-module)
6. [Queue Manager](#queue-manager)
7. [Configuration](#configuration)
8. [Data Models](#data-models)
9. [Utilities](#utilities)

---

## Core API

### `ChronosArchiver`

Main archiver class orchestrating the 4-stage pipeline.

```python
from chronos_archiver import ChronosArchiver

archiver = ChronosArchiver(config)
```

#### Methods

##### `__init__(config: dict) -> None`

Initialize ChronosArchiver with configuration.

**Parameters**:
- `config` (dict): Configuration dictionary

**Example**:
```python
config = load_config('config.yaml')
archiver = ChronosArchiver(config)
```

##### `async archive_url(url: str) -> None`

Archive a single URL through the complete pipeline.

**Parameters**:
- `url` (str): Wayback Machine URL to archive

**Example**:
```python
await archiver.archive_url(
    'https://web.archive.org/web/20090430060114/http://www.dar.org.br/'
)
```

##### `async archive_urls(urls: list[str]) -> None`

Archive multiple URLs concurrently.

**Parameters**:
- `urls` (list[str]): List of Wayback Machine URLs

**Example**:
```python
urls = [
    'https://web.archive.org/web/20090430060114/http://www.dar.org.br/',
    'https://web.archive.org/web/20120302052501/http://www.dar.org.br/',
]
await archiver.archive_urls(urls)
```

##### `async start_workers(worker_count: int = 4) -> None`

Start background workers for async processing.

**Parameters**:
- `worker_count` (int): Number of workers to start (default: 4)

##### `async shutdown() -> None`

Gracefully shutdown the archiver and all workers.

---

## Discovery Module

### `WaybackDiscovery`

Discover archived URLs using the Wayback Machine CDX API.

```python
from chronos_archiver.discovery import WaybackDiscovery

discovery = WaybackDiscovery(config)
```

#### Methods

##### `async find_snapshots(url: str) -> list[ArchiveSnapshot]`

Find all snapshots for a given URL or URL pattern.

**Parameters**:
- `url` (str): URL or Wayback Machine URL

**Returns**:
- `list[ArchiveSnapshot]`: List of discovered snapshots

**Example**:
```python
snapshots = await discovery.find_snapshots('http://www.dar.org.br/')
for snapshot in snapshots:
    print(f"{snapshot.timestamp}: {snapshot.url}")
```

##### `async batch_discover(urls: list[str]) -> list[ArchiveSnapshot]`

Discover snapshots for multiple URLs concurrently.

**Parameters**:
- `urls` (list[str]): List of URLs

**Returns**:
- `list[ArchiveSnapshot]`: Combined list of all snapshots

---

## Ingestion Module

### `ContentIngestion`

Download and validate content from the Wayback Machine.

```python
from chronos_archiver.ingestion import ContentIngestion

ingestion = ContentIngestion(config)
```

#### Methods

##### `async download(snapshot: ArchiveSnapshot) -> Optional[DownloadedContent]`

Download content for a snapshot.

**Parameters**:
- `snapshot` (ArchiveSnapshot): Snapshot to download

**Returns**:
- `Optional[DownloadedContent]`: Downloaded content or None if failed

**Example**:
```python
content = await ingestion.download(snapshot)
if content:
    print(f"Downloaded {len(content.content)} bytes")
```

##### `async batch_download(snapshots: list[ArchiveSnapshot], concurrency: int = 10) -> list[Optional[DownloadedContent]]`

Download multiple snapshots concurrently.

**Parameters**:
- `snapshots` (list[ArchiveSnapshot]): Snapshots to download
- `concurrency` (int): Maximum concurrent downloads (default: 10)

**Returns**:
- `list[Optional[DownloadedContent]]`: List of downloaded content

---

## Transformation Module

### `ContentTransformation`

Transform content for local archiving.

```python
from chronos_archiver.transformation import ContentTransformation

transformation = ContentTransformation(config)
```

#### Methods

##### `async transform(downloaded: DownloadedContent) -> Optional[TransformedContent]`

Transform downloaded content.

**Parameters**:
- `downloaded` (DownloadedContent): Downloaded content

**Returns**:
- `Optional[TransformedContent]`: Transformed content or None if failed

**Example**:
```python
transformed = await transformation.transform(downloaded)
if transformed:
    print(f"Title: {transformed.metadata.get('title')}")
    print(f"Links: {len(transformed.links)}")
```

---

## Indexing Module

### `ContentIndexer`

Index and store archived content.

```python
from chronos_archiver.indexing import ContentIndexer

indexer = ContentIndexer(config)
```

#### Methods

##### `async index(transformed: TransformedContent) -> Optional[IndexedContent]`

Index transformed content.

**Parameters**:
- `transformed` (TransformedContent): Transformed content

**Returns**:
- `Optional[IndexedContent]`: Indexed content or None if failed

**Example**:
```python
indexed = await indexer.index(transformed)
if indexed:
    print(f"Indexed with ID: {indexed.id}")
```

##### `async search(query: str, limit: int = 100) -> list[IndexedContent]`

Search indexed content.

**Parameters**:
- `query` (str): Search query
- `limit` (int): Maximum results (default: 100)

**Returns**:
- `list[IndexedContent]`: Matching indexed content

**Example**:
```python
results = await indexer.search("Diocese Anglicana", limit=10)
for result in results:
    print(result.metadata.get('title'))
```

---

## Queue Manager

### `QueueManager`

Manage message queues for async processing.

```python
from chronos_archiver.queue_manager import QueueManager

queue_manager = QueueManager(config)
```

#### Methods

##### `async connect() -> None`

Connect to queue backend.

##### `async disconnect() -> None`

Disconnect from queue backend.

##### `async enqueue(queue_name: str, message_type: str, payload: dict) -> str`

Add a message to a queue.

**Parameters**:
- `queue_name` (str): Queue name
- `message_type` (str): Message type
- `payload` (dict): Message payload

**Returns**:
- `str`: Message ID

##### `async dequeue(queue_name: str, timeout: int = 0) -> Optional[QueueMessage]`

Remove and return a message from a queue.

**Parameters**:
- `queue_name` (str): Queue name
- `timeout` (int): Blocking timeout in seconds

**Returns**:
- `Optional[QueueMessage]`: Message or None

---

## Configuration

### `load_config(config_path: Optional[str] = None) -> dict`

Load configuration from YAML file.

**Parameters**:
- `config_path` (Optional[str]): Path to config file

**Returns**:
- `dict`: Configuration dictionary

**Example**:
```python
from chronos_archiver.config import load_config

config = load_config('config.yaml')
```

### `save_config(config: dict, config_path: str) -> None`

Save configuration to YAML file.

**Parameters**:
- `config` (dict): Configuration dictionary
- `config_path` (str): Path to save file

---

## Data Models

All data models use Pydantic for validation.

### `ArchiveSnapshot`

```python
class ArchiveSnapshot(BaseModel):
    url: str
    original_url: str
    timestamp: str
    mime_type: Optional[str]
    status_code: Optional[int]
    digest: Optional[str]
    length: Optional[int]
    status: ArchiveStatus
```

### `DownloadedContent`

```python
class DownloadedContent(BaseModel):
    snapshot: ArchiveSnapshot
    content: bytes
    headers: dict[str, str]
    encoding: Optional[str]
```

### `TransformedContent`

```python
class TransformedContent(BaseModel):
    snapshot: ArchiveSnapshot
    content: str
    text_content: Optional[str]
    metadata: dict[str, Any]
    links: list[str]
```

### `IndexedContent`

```python
class IndexedContent(BaseModel):
    id: Optional[int]
    snapshot: ArchiveSnapshot
    content: str
    text_content: Optional[str]
    metadata: dict[str, Any]
```

---

## Utilities

### URL Utilities

```python
from chronos_archiver.utils import (
    parse_wayback_url,
    build_wayback_url,
    normalize_url,
    is_valid_url,
)

# Parse Wayback URL
parsed = parse_wayback_url(
    'https://web.archive.org/web/20090430060114/http://www.dar.org.br/'
)
# Returns: {'timestamp': '20090430060114', 'original_url': 'http://www.dar.org.br/'}

# Build Wayback URL
url = build_wayback_url('20090430060114', 'http://www.dar.org.br/')
# Returns: 'https://web.archive.org/web/20090430060114/http://www.dar.org.br/'
```

### Logging

```python
from chronos_archiver.utils import setup_logging

logger = setup_logging(config)
logger.info("Started archiving")
```

---

**Last Updated**: January 2026  
**Version**: 1.0.0