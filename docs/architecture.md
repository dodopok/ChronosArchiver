# ChronosArchiver Architecture

This document provides a detailed overview of the ChronosArchiver system architecture.

## Table of Contents

1. [System Overview](#system-overview)
2. [Pipeline Architecture](#pipeline-architecture)
3. [Component Details](#component-details)
4. [Data Flow](#data-flow)
5. [Scalability](#scalability)
6. [Technology Stack](#technology-stack)

## System Overview

ChronosArchiver is built as a multi-stage asynchronous pipeline system designed to efficiently archive websites from the Internet Archive's Wayback Machine. The system emphasizes:

- **Modularity**: Each stage is independently testable and replaceable
- **Scalability**: Horizontal scaling via worker processes
- **Reliability**: Retry logic, error handling, and data validation
- **Performance**: Async I/O and concurrent processing

## Pipeline Architecture

### 4-Stage Pipeline

```
┌─────────────────────────────────────────────────────────────────────┐
│                        ChronosArchiver Pipeline                      │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────┐       ┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│              │       │              │       │              │       │              │
│  Discovery   │──────>│  Ingestion   │──────>│Transformation│──────>│   Indexing   │
│              │       │              │       │              │       │              │
└──────────────┘       └──────────────┘       └──────────────┘       └──────────────┘
       │                      │                      │                      │
       v                      v                      v                      v
   [Queue 1]              [Queue 2]              [Queue 3]              [Database]
   Discovery              Ingestion           Transformation            + Filesystem
```

### Message Queue Integration

Each stage communicates via message queues (Redis by default):

```python
# Asynchronous message flow
Discovery -> [discovery_queue] -> Ingestion Worker
Ingestion -> [ingestion_queue] -> Transformation Worker  
Transformation -> [transformation_queue] -> Indexing Worker
```

## Component Details

### 1. Discovery Module (`discovery.py`)

**Purpose**: Find and identify URLs to archive

**Key Features**:
- CDX API integration
- URL pattern matching
- Snapshot deduplication
- Batch discovery

**Process**:
1. Query Wayback Machine CDX API
2. Parse JSON responses
3. Filter by status code and MIME type
4. Deduplicate by content digest
5. Create `ArchiveSnapshot` objects

**Example CDX Query**:
```
GET https://web.archive.org/cdx/search/cdx
  ?url=example.com
  &output=json
  &fl=timestamp,original,mimetype,statuscode,digest,length
```

### 2. Ingestion Module (`ingestion.py`)

**Purpose**: Download content from Wayback Machine

**Key Features**:
- Async HTTP downloads
- Rate limiting (throttling)
- Content validation
- Retry logic with exponential backoff
- Size limits

**Process**:
1. Fetch URL from Wayback Machine
2. Validate content size
3. Verify content hash (if available)
4. Sanitize downloaded content
5. Create `DownloadedContent` object

**Rate Limiting**:
```python
default: 5 requests/second
concurrent: 10 simultaneous connections
```

### 3. Transformation Module (`transformation.py`)

**Purpose**: Transform content for local archiving

**Key Features**:
- HTML parsing with BeautifulSoup
- Link rewriting
- Metadata extraction
- Text extraction
- Content cleaning

**Process**:
1. Decode HTML content
2. Parse with BeautifulSoup
3. Rewrite links to local/archived versions
4. Extract metadata (title, description, etc.)
5. Extract plain text for search
6. Clean and normalize HTML
7. Create `TransformedContent` object

**Link Rewriting**:
```html
<!-- Original -->
<a href="/page.html">Link</a>

<!-- Rewritten -->
<a href="/20090430060114/http://example.com/page.html">Link</a>
```

### 4. Indexing Module (`indexing.py`)

**Purpose**: Store and index content

**Key Features**:
- SQLite/PostgreSQL storage
- File system organization
- Content compression
- Full-text search
- Metadata indexing

**Process**:
1. Generate file path (organized by date)
2. Compress content (optional)
3. Write to file system
4. Store metadata in database
5. Create searchable index
6. Return `IndexedContent` object

**File Organization**:
```
archive/
├── content/
│   ├── 2009/
│   │   ├── 04/
│   │   │   └── 30/
│   │   │       └── 20090430060114_www.dar.org.br_.html.gz
│   ├── 2012/
│   └── 2015/
└── chronos.db
```

### 5. Queue Manager (`queue_manager.py`)

**Purpose**: Manage async message queues

**Key Features**:
- Redis backend support
- Worker management
- Message routing
- Retry handling
- Queue monitoring

**Worker Model**:
```python
Worker Process:
1. Poll queues in order (discovery -> ingestion -> transformation -> indexing)
2. Process message with appropriate handler
3. On success: dequeue message
4. On failure: retry up to max_attempts
5. Repeat
```

## Data Flow

### Complete Archive Flow

```
1. User Input
   ↓
2. Discovery
   - Query CDX API
   - Create ArchiveSnapshot objects
   ↓
3. Queue → discovery_queue
   ↓
4. Ingestion Worker
   - Download content
   - Validate and sanitize
   - Create DownloadedContent
   ↓
5. Queue → ingestion_queue
   ↓
6. Transformation Worker
   - Parse HTML
   - Rewrite links
   - Extract metadata
   - Create TransformedContent
   ↓
7. Queue → transformation_queue
   ↓
8. Indexing Worker
   - Store to filesystem
   - Index in database
   - Create IndexedContent
   ↓
9. Complete!
```

### Data Models

```python
ArchiveSnapshot
├── url: str
├── original_url: str
├── timestamp: str
├── mime_type: str
├── status_code: int
├── digest: str
└── status: ArchiveStatus

DownloadedContent
├── snapshot: ArchiveSnapshot
├── content: bytes
├── headers: dict
└── encoding: str

TransformedContent
├── snapshot: ArchiveSnapshot
├── content: str (transformed HTML)
├── text_content: str
├── metadata: dict
└── links: list[str]

IndexedContent
├── id: int
├── snapshot: ArchiveSnapshot
├── content: str
├── text_content: str
└── metadata: dict
```

## Scalability

### Horizontal Scaling

```
┌─────────────────────────────────────────────────┐
│              Load Balancer / Queue              │
└─────────────────────────────────────────────────┘
          │              │              │
    ┌─────┴─────┐  ┌─────┴─────┐  ┌─────┴─────┐
    │  Worker 1 │  │  Worker 2 │  │  Worker N │
    │           │  │           │  │           │
    │  All 4    │  │  All 4    │  │  All 4    │
    │  Stages   │  │  Stages   │  │  Stages   │
    └───────────┘  └───────────┘  └───────────┘
          │              │              │
    ┌─────┴──────────────┴──────────────┴─────┐
    │          Shared Database & Storage       │
    └──────────────────────────────────────────┘
```

### Performance Optimizations

1. **Async I/O**: All network operations use `asyncio`
2. **Connection Pooling**: Reuse HTTP connections
3. **Batch Processing**: Process multiple items concurrently
4. **Rate Limiting**: Prevent overwhelming source servers
5. **Content Compression**: Reduce storage requirements
6. **Database Indexing**: Fast lookups by URL, timestamp, digest

## Technology Stack

### Core Libraries

- **Python 3.8+**: Modern async/await syntax
- **aiohttp**: Async HTTP client
- **asyncio**: Async I/O framework
- **BeautifulSoup4**: HTML parsing
- **SQLAlchemy**: Database ORM
- **Redis**: Message queue backend
- **Pydantic**: Data validation
- **Click**: CLI framework

### Optional Components

- **PostgreSQL**: Production database
- **RabbitMQ**: Alternative queue backend
- **Prometheus**: Metrics collection
- **Docker**: Containerization

## Configuration

All components are configurable via `config.yaml`:

```yaml
processing:
  workers: 4                    # Concurrent workers
  batch_size: 10               # Items per batch
  requests_per_second: 5       # Rate limit
  concurrent_requests: 10      # Max simultaneous
```

## Error Handling

### Retry Strategy

```python
Retry Logic:
- Initial delay: 5 seconds
- Backoff multiplier: 2x
- Max attempts: 3

Example:
  Attempt 1: Immediate
  Attempt 2: 5 seconds
  Attempt 3: 10 seconds
  Final: Mark as failed
```

### Failure Recovery

1. Log all errors with context
2. Update status to FAILED
3. Store partial results if possible
4. Continue processing other items
5. Generate failure report

## Security Considerations

1. **Input Validation**: All URLs validated
2. **Content Sanitization**: Remove null bytes, malicious scripts
3. **Size Limits**: Prevent memory exhaustion
4. **SSL Verification**: Enabled by default
5. **User Agent**: Identifies the archiver

## Future Enhancements

1. **Incremental Archiving**: Only download changed content
2. **Distributed Processing**: Multi-machine deployments
3. **Advanced Search**: Full-text indexing with Elasticsearch
4. **Web UI**: Browser-based interface
5. **WARC Export**: Standard archive format
6. **Kubernetes**: Container orchestration

---

**Last Updated**: January 2026  
**Version**: 1.0.0