# ChronosArchiver API Reference

Complete API documentation for all public classes, methods, and functions.

## Table of Contents

- [Core Classes](#core-classes)
- [Discovery Module](#discovery-module)
- [Ingestion Module](#ingestion-module)
- [Transformation Module](#transformation-module)
- [Indexing Module](#indexing-module)
- [Queue Manager](#queue-manager)
- [Configuration](#configuration)
- [Models](#models)
- [Utilities](#utilities)

## Core Classes

### ChronosArchiver

Main orchestrator class for the archival pipeline.

```python
from chronos_archiver import ChronosArchiver
from chronos_archiver.config import load_config

config = load_config()
archiver = ChronosArchiver(config)
```

#### Methods

##### `__init__(config: dict) -> None`

Initialize the archiver with configuration.

**Parameters**:
- `config` (dict): Configuration dictionary

**Example**:
```python
config = {"archive": {"output_dir": "./archive"}}
archiver = ChronosArchiver(config)
```

##### `async archive_url(url: str) -> None`

Archive a single URL through the complete pipeline.

**Parameters**:
- `url` (str): Wayback Machine URL to archive

**Example**:
```python
await archiver.archive_url(
    "https://web.archive.org/web/20090430060114/http://www.dar.org.br/"
)
```

##### `async archive_urls(urls: list[str]) -> None`

Archive multiple URLs concurrently.

**Parameters**:
- `urls` (list[str]): List of Wayback Machine URLs

**Example**:
```python
urls = [
    "https://web.archive.org/web/20090430060114/http://www.dar.org.br/",
    "https://web.archive.org/web/20120302052501/http://www.dar.org.br/",
]
await archiver.archive_urls(urls)
```

##### `async start_workers(worker_count: int = 4) -> None`

Start background workers for async processing.

**Parameters**:
- `worker_count` (int): Number of workers to start

**Example**:
```python
await archiver.start_workers(worker_count=8)
```

##### `async shutdown() -> None`

Gracefully shutdown the archiver and all workers.

**Example**:
```python
await archiver.shutdown()
```

## Discovery Module

### WaybackDiscovery

Discover archived URLs using the Wayback Machine CDX API.

```python
from chronos_archiver.discovery import WaybackDiscovery

discovery = WaybackDiscovery(config)
```

#### Methods

##### `async find_snapshots(url: str) -> list[ArchiveSnapshot]`

Find all snapshots for a given URL.

**Parameters**:
- `url` (str): URL or Wayback Machine URL

**Returns**:
- `list[ArchiveSnapshot]`: List of discovered snapshots

**Example**:
```python
snapshots = await discovery.find_snapshots("http://www.dar.org.br/")
for snapshot in snapshots:
    print(f"{snapshot.timestamp}: {snapshot.url}")
```

##### `async discover_site(base_url: str, max_depth: int = 3) -> list[ArchiveSnapshot]`

Discover all pages from a site by crawling links.

**Parameters**:
- `base_url` (str): Base URL to start discovery
- `max_depth` (int): Maximum crawl depth

**Returns**:
- `list[ArchiveSnapshot]`: All discovered snapshots

**Example**:
```python
snapshots = await discovery.discover_site(
    "http://www.dar.org.br/",
    max_depth=2
)
```

##### `async batch_discover(urls: list[str]) -> list[ArchiveSnapshot]`

Discover snapshots for multiple URLs concurrently.

**Parameters**:
- `urls` (list[str]): List of URLs

**Returns**:
- `list[ArchiveSnapshot]`: Combined list of snapshots

**Example**:
```python
urls = ["http://www.dar.org.br/", "http://www.ieab.org.br/"]
snapshots = await discovery.batch_discover(urls)
```

## Ingestion Module

### ContentIngestion

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
- `snapshots` (list[ArchiveSnapshot]): List of snapshots
- `concurrency` (int): Maximum concurrent downloads

**Returns**:
- `list[Optional[DownloadedContent]]`: List of downloaded content

**Example**:
```python
contents = await ingestion.batch_download(snapshots, concurrency=20)
successful = [c for c in contents if c is not None]
```

##### `sanitize_content(content: bytes) -> bytes`

Sanitize downloaded content.

**Parameters**:
- `content` (bytes): Raw content bytes

**Returns**:
- `bytes`: Sanitized content

**Example**:
```python
clean = ingestion.sanitize_content(raw_content)
```

## Transformation Module

### ContentTransformation

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

## Indexing Module

### ContentIndexer

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
- `limit` (int): Maximum results

**Returns**:
- `list[IndexedContent]`: Matching indexed content

**Example**:
```python
results = await indexer.search("Diocese Anglicana", limit=10)
for result in results:
    print(result.metadata.get("title"))
```

##### `async close() -> None`

Close database connections.

**Example**:
```python
await indexer.close()
```

## Queue Manager

### QueueManager

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
- `queue_name` (str): Name of the queue
- `message_type` (str): Type of message
- `payload` (dict): Message payload

**Returns**:
- `str`: Message ID

##### `async dequeue(queue_name: str, timeout: int = 0) -> Optional[QueueMessage]`

Remove and return a message from a queue.

**Parameters**:
- `queue_name` (str): Name of the queue
- `timeout` (int): Blocking timeout in seconds

**Returns**:
- `Optional[QueueMessage]`: Message or None

##### `async queue_size(queue_name: str) -> int`

Get the size of a queue.

##### `async clear_queue(queue_name: str) -> None`

Clear all messages from a queue.

## Configuration

### load_config

Load configuration from YAML file.

```python
from chronos_archiver.config import load_config

config = load_config("config.yaml")
```

**Parameters**:
- `config_path` (Optional[str]): Path to configuration file

**Returns**:
- `dict`: Configuration dictionary

### save_config

Save configuration to YAML file.

```python
from chronos_archiver.config import save_config

save_config(config, "config.yaml")
```

### get_default_config

Get default configuration.

```python
from chronos_archiver.config import get_default_config

config = get_default_config()
```

## Models

### ArchiveSnapshot

Represents a snapshot from the Wayback Machine.

**Fields**:
- `url` (str): Wayback Machine URL
- `original_url` (str): Original URL
- `timestamp` (str): Snapshot timestamp
- `mime_type` (Optional[str]): MIME type
- `status_code` (Optional[int]): HTTP status code
- `digest` (Optional[str]): Content digest
- `length` (Optional[int]): Content length
- `status` (ArchiveStatus): Processing status

### DownloadedContent

Represents downloaded content.

**Fields**:
- `snapshot` (ArchiveSnapshot): Associated snapshot
- `content` (bytes): Raw content
- `headers` (dict): HTTP headers
- `encoding` (Optional[str]): Content encoding

### TransformedContent

Represents transformed content.

**Fields**:
- `snapshot` (ArchiveSnapshot): Associated snapshot
- `content` (str): Transformed HTML
- `text_content` (Optional[str]): Extracted text
- `metadata` (dict): Extracted metadata
- `links` (list[str]): Extracted links

### IndexedContent

Represents indexed content.

**Fields**:
- `id` (Optional[int]): Database ID
- `snapshot` (ArchiveSnapshot): Associated snapshot
- `content` (str): Stored content
- `text_content` (Optional[str]): Searchable text
- `metadata` (dict): Metadata

## Utilities

### parse_wayback_url

Parse a Wayback Machine URL.

```python
from chronos_archiver.utils import parse_wayback_url

parsed = parse_wayback_url(
    "https://web.archive.org/web/20090430060114/http://www.dar.org.br/"
)
print(parsed["timestamp"])  # "20090430060114"
print(parsed["original_url"])  # "http://www.dar.org.br/"
```

### build_wayback_url

Build a Wayback Machine URL.

```python
from chronos_archiver.utils import build_wayback_url

url = build_wayback_url("20090430060114", "http://www.dar.org.br/")
# "https://web.archive.org/web/20090430060114/http://www.dar.org.br/"
```

### normalize_url

Normalize a URL for consistent comparison.

```python
from chronos_archiver.utils import normalize_url

normalized = normalize_url("HTTP://EXAMPLE.COM:80/")
# "http://example.com"
```

### calculate_hash

Calculate hash of content.

```python
from chronos_archiver.utils import calculate_hash

hash_value = calculate_hash(content, "sha256")
```

### format_bytes

Format byte size in human-readable format.

```python
from chronos_archiver.utils import format_bytes

print(format_bytes(1024 * 1024))  # "1.0 MB"
```