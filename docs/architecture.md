# ChronosArchiver Architecture

This document provides a detailed overview of ChronosArchiver's architecture, design decisions, and implementation details.

## Table of Contents

- [System Overview](#system-overview)
- [Pipeline Architecture](#pipeline-architecture)
- [Component Details](#component-details)
- [Data Flow](#data-flow)
- [Scalability](#scalability)
- [Performance Considerations](#performance-considerations)

## System Overview

ChronosArchiver is designed as a modular, asynchronous archival system that processes web pages through a four-stage pipeline. The system emphasizes:

- **Modularity**: Each stage is independent and can be tested/deployed separately
- **Asynchronicity**: Heavy use of `asyncio` for I/O-bound operations
- **Scalability**: Message queue-based architecture for distributed processing
- **Reliability**: Retry mechanisms, error handling, and data validation
- **Extensibility**: Plugin architecture for custom processors

### High-Level Architecture

```
┌───────────────────────────────────────────────────┐
│                 ChronosArchiver                          │
│                                                          │
│  ┌─────────────────────────────────────────┐  │
│  │            4-Stage Pipeline                  │  │
│  │                                              │  │
│  │  Discovery → Ingestion → Transform → Index  │  │
│  └─────────────────────────────────────────┘  │
│                     │                                    │
│                     │                                    │
│  ┌─────────────────────────────────────────┐  │
│  │          Queue Manager                    │  │
│  │                                              │  │
│  │  Redis/RabbitMQ Message Queues            │  │
│  └─────────────────────────────────────────┘  │
│                                                          │
└───────────────────────────────────────────────────┘
         │                              │
         │                              │
    ┌────┴────┐                    ┌────┴─────┐
    │  Redis  │                    │ Database │
    └─────────┘                    └──────────┘
```

## Pipeline Architecture

### Stage 1: Discovery

**Purpose**: Find and catalog all available snapshots for target URLs

**Input**: URL or URL pattern

**Output**: List of `ArchiveSnapshot` objects

**Components**:
- CDX API client
- URL parser
- Deduplication logic
- Status code filter

**Process**:
1. Parse input URL (Wayback URL or original URL)
2. Query CDX API for all snapshots
3. Parse CDX response (JSON format)
4. Filter by status codes (default: 200, 301, 302)
5. Deduplicate by content digest
6. Create `ArchiveSnapshot` objects

**Key Features**:
- Handles both Wayback URLs and original URLs
- Supports wildcard/prefix matching
- Configurable filters
- Pagination support for large result sets

### Stage 2: Ingestion

**Purpose**: Download content from the Wayback Machine

**Input**: `ArchiveSnapshot` object

**Output**: `DownloadedContent` object

**Components**:
- Async HTTP client (`aiohttp`)
- Rate limiter (throttling)
- Retry mechanism
- Content validator

**Process**:
1. Apply rate limiting
2. Send HTTP GET request to Wayback URL
3. Validate response headers
4. Check file size limits
5. Download content
6. Verify content hash (if available)
7. Sanitize content

**Key Features**:
- Automatic retries with exponential backoff
- Rate limiting to respect Wayback Machine
- File size limits
- Content hash verification
- Connection pooling

### Stage 3: Transformation

**Purpose**: Transform content for local archival

**Input**: `DownloadedContent` object

**Output**: `TransformedContent` object

**Components**:
- HTML parser (BeautifulSoup)
- Link rewriter
- Metadata extractor
- Text extractor

**Process**:
1. Decode content (handle various encodings)
2. Parse HTML with BeautifulSoup
3. Rewrite links:
   - Convert relative to absolute
   - Prefix with Wayback timestamp
   - Make relative to archive root
4. Extract metadata:
   - Title, description, keywords
   - Open Graph tags
   - Language
5. Extract plain text for search
6. Extract all links
7. Optional: remove scripts, comments

**Key Features**:
- Preserves link structure
- Handles various URL formats
- CSS url() rewriting
- Encoding fallback
- Configurable transformations

### Stage 4: Indexing

**Purpose**: Store and index content for retrieval

**Input**: `TransformedContent` object

**Output**: `IndexedContent` object

**Components**:
- File storage system
- Database (SQLAlchemy)
- Compression (gzip)
- Search index

**Process**:
1. Generate file path (date-based structure)
2. Optionally compress content
3. Write to filesystem
4. Extract searchable fields
5. Store metadata in database
6. Update search index

**Key Features**:
- Date-based directory organization
- Optional compression
- Full-text search
- Metadata indexing
- SQLite or PostgreSQL support

## Component Details

### Queue Manager

**Purpose**: Coordinate async processing across stages

**Implementation**: Redis-backed message queues

**Queues**:
- `chronos:discovery` - URLs to discover
- `chronos:ingestion` - Snapshots to download
- `chronos:transformation` - Content to transform
- `chronos:indexing` - Content to index

**Features**:
- Message persistence
- Retry logic with retry count
- TTL for messages
- Worker pool management
- Graceful shutdown

### Configuration System

**Implementation**: YAML-based with Pydantic validation

**Structure**:
```yaml
archive:
  output_dir: "./archive"
  user_agent: "ChronosArchiver/1.0"

queue:
  backend: "redis"
  redis_url: "redis://localhost:6379/0"

processing:
  workers: 4
  retry_attempts: 3

database:
  type: "sqlite"
  sqlite_path: "./archive/chronos.db"
```

**Validation**: Pydantic models ensure type safety and defaults

### Data Models

**Pydantic Models**:
- `ArchiveSnapshot` - Snapshot metadata
- `DownloadedContent` - Raw downloaded data
- `TransformedContent` - Processed content
- `IndexedContent` - Stored content
- `QueueMessage` - Inter-stage messages
- `ProcessingStats` - Pipeline statistics

**Database Models** (SQLAlchemy):
- `ArchivedPage` - Indexed page record

## Data Flow

### Synchronous Mode

```
User Input
    ↓
Discovery → Snapshots
    ↓
Ingestion → Content
    ↓
Transformation → Transformed
    ↓
Indexing → Stored
    ↓
Result to User
```

### Asynchronous Mode

```
User Input
    ↓
Discovery → Queue 1
                ↓
            Worker Pool
                ↓
            Ingestion → Queue 2
                        ↓
                    Worker Pool
                        ↓
                    Transformation → Queue 3
                                    ↓
                                Worker Pool
                                    ↓
                                Indexing → Database
```

## Scalability

### Horizontal Scaling

**Worker Nodes**:
- Multiple workers can process queues concurrently
- Deploy workers on separate machines
- Redis handles distribution

**Docker Deployment**:
```yaml
services:
  worker:
    image: chronos-archiver
    deploy:
      replicas: 5
```

### Vertical Scaling

**Resource Tuning**:
- Increase worker count per node
- Adjust concurrent request limits
- Tune connection pool sizes

**Configuration**:
```yaml
processing:
  workers: 8
  concurrent_requests: 20
  batch_size: 50
```

### Database Scaling

**SQLite** (Development):
- Single-file database
- Limited concurrency
- Good for < 1M records

**PostgreSQL** (Production):
- Full concurrency support
- Replication
- Partitioning for large datasets

## Performance Considerations

### Bottlenecks

1. **Network I/O**: Downloading from Wayback Machine
   - Solution: Increase concurrent requests, use connection pooling

2. **Parsing**: HTML parsing with BeautifulSoup
   - Solution: Use lxml parser, consider parallel processing

3. **Database Writes**: Indexing operations
   - Solution: Batch inserts, use PostgreSQL, optimize indexes

### Optimizations

**Async I/O**:
```python
# Bad: Sequential
for url in urls:
    await download(url)

# Good: Concurrent
await asyncio.gather(*[download(url) for url in urls])
```

**Connection Pooling**:
```python
async with aiohttp.ClientSession() as session:
    # Reuse connections
    for url in urls:
        await session.get(url)
```

**Batch Processing**:
```python
# Process in batches of 10
for batch in chunks(snapshots, 10):
    await process_batch(batch)
```

### Memory Management

**Streaming**:
- Stream large files instead of loading into memory
- Use generators for large result sets

**Limits**:
- File size limits (default: 100MB)
- Queue size limits
- Worker count limits

## Error Handling

### Retry Strategy

```python
max_attempts = 3
delay = 5  # seconds
backoff = 2  # exponential

for attempt in range(max_attempts):
    try:
        return await operation()
    except Exception:
        if attempt < max_attempts - 1:
            await asyncio.sleep(delay * (backoff ** attempt))
```

### Failure Recovery

- Failed messages re-queued with retry count
- Persistent queues survive crashes
- Database transactions for atomicity
- Logging for debugging

## Monitoring

### Metrics

- Queue sizes
- Processing throughput
- Error rates
- Download speeds
- Storage usage

### Logging

```python
logger.info(f"Processing snapshot: {snapshot.url}")
logger.error(f"Download failed: {error}")
logger.warning(f"Large file skipped: {size}")
```

### Health Checks

- Redis connectivity
- Database connectivity
- Disk space
- Worker status

## Security Considerations

### Input Validation

- Validate URLs before processing
- Sanitize filenames
- Limit file sizes

### Content Safety

- Remove null bytes
- Validate content types
- Sandbox execution (future)

### Authentication

- No authentication required for Wayback Machine
- Optional auth for internal deployments

## Future Enhancements

1. **WARC Format Support**: Export to standard WARC format
2. **Incremental Archiving**: Only archive new snapshots
3. **Web UI**: Browse archived content
4. **Full-Text Search**: Elasticsearch integration
5. **CDN Support**: Distribute archived content
6. **Webhooks**: Notify on completion
7. **API**: RESTful API for programmatic access