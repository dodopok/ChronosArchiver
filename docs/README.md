# ChronosArchiver Documentation

Welcome to the ChronosArchiver documentation!

## Documentation Index

### Getting Started

- **[Main README](../README.md)** - Project overview, quick start, and installation
- **[Usage Guide](usage.md)** - Comprehensive usage guide with examples
- **[Contributing Guidelines](../CONTRIBUTING.md)** - How to contribute to the project

### Technical Documentation

- **[Architecture Guide](architecture.md)** - Detailed system architecture and design
- **[API Reference](api.md)** - Complete API documentation
- **[Configuration Reference](#configuration-reference)** - All configuration options

### Examples

- **[Basic Examples](../examples/basic_usage.py)** - Simple usage examples
- **[Advanced Examples](../examples/advanced_usage.py)** - Advanced usage patterns
- **[Sample Sites](../examples/sample_sites.txt)** - Test URLs

## Quick Links

### For Users

1. **Installation**: See [README - Installation](../README.md#installation)
2. **Quick Start**: See [README - Quick Start](../README.md#quick-start)
3. **Basic Usage**: See [Usage Guide - Basic Usage](usage.md#basic-usage)
4. **CLI Reference**: See [Usage Guide - CLI Reference](usage.md#cli-reference)
5. **Troubleshooting**: See [Usage Guide - Troubleshooting](usage.md#troubleshooting)

### For Developers

1. **Architecture Overview**: See [Architecture Guide](architecture.md)
2. **API Documentation**: See [API Reference](api.md)
3. **Contributing**: See [Contributing Guidelines](../CONTRIBUTING.md)
4. **Running Tests**: See [Contributing - Development](../CONTRIBUTING.md#development-guidelines)

## Configuration Reference

### Archive Settings

```yaml
archive:
  output_dir: "./archive"           # Output directory
  user_agent: "ChronosArchiver/1.0"  # User agent string
  max_file_size: 100                 # Max file size in MB
  allowed_mime_types:                # Filter by MIME types (empty = all)
    - "text/html"
    - "text/css"
    - "application/javascript"
```

### Queue Settings

```yaml
queue:
  backend: "redis"                              # Queue backend
  redis_url: "redis://localhost:6379/0"        # Redis connection URL
  discovery_queue: "chronos:discovery"          # Queue names
  ingestion_queue: "chronos:ingestion"
  transformation_queue: "chronos:transformation"
  indexing_queue: "chronos:indexing"
  max_queue_size: 10000                         # Max messages per queue
  message_ttl: 86400                            # Message TTL in seconds
```

### Processing Settings

```yaml
processing:
  workers: 4                    # Number of workers per stage
  batch_size: 10                # Batch size for processing
  retry_attempts: 3             # Max retry attempts
  retry_delay: 5                # Initial retry delay (seconds)
  retry_backoff: 2              # Exponential backoff multiplier
  requests_per_second: 5        # Rate limit (requests/second)
  concurrent_requests: 10       # Max concurrent requests
  request_timeout: 30           # Request timeout (seconds)
  download_timeout: 300         # Download timeout (seconds)
```

### Database Settings

```yaml
database:
  type: "sqlite"                                    # Database type
  sqlite_path: "./archive/chronos.db"              # SQLite path
  # postgresql_url: "postgresql://..."              # PostgreSQL URL
  pool_size: 5                                      # Connection pool size
  max_overflow: 10                                  # Max overflow connections
```

### Discovery Settings

```yaml
discovery:
  cdx_api_url: "https://web.archive.org/cdx/search/cdx"
  cdx_params:
    output: "json"
    fl: "timestamp,original,mimetype,statuscode,digest,length"
  filter_status_codes: [200, 301, 302]  # Filter by HTTP status
  deduplicate_snapshots: true           # Remove duplicates by digest
```

### Ingestion Settings

```yaml
ingestion:
  wayback_url: "https://web.archive.org/web"
  verify_ssl: true                 # Verify SSL certificates
  follow_redirects: true           # Follow HTTP redirects
  validate_mime_type: true         # Validate MIME types
  validate_content_hash: true      # Validate content hashes
```

### Transformation Settings

```yaml
transformation:
  rewrite_links: true             # Rewrite links for local archival
  make_links_relative: true       # Make links relative
  extract_metadata: true          # Extract metadata
  extract_text: true              # Extract plain text
  prettify_html: false            # Prettify HTML output
  remove_scripts: false           # Remove script tags
  remove_comments: true           # Remove HTML comments
```

### Indexing Settings

```yaml
indexing:
  enable_full_text_search: true   # Enable search
  index_fields:                   # Fields to index
    - "url"
    - "title"
    - "timestamp"
    - "content"
    - "metadata"
  compress_content: true          # Compress stored content
  compression_level: 6            # gzip compression level (1-9)
```

### Logging Settings

```yaml
logging:
  level: "INFO"                       # Log level
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  log_to_file: true                   # Enable file logging
  log_file: "./logs/chronos.log"     # Log file path
  rotate_logs: true                   # Enable log rotation
  max_log_size: 10485760              # Max log size (bytes)
  backup_count: 5                     # Number of backup logs
```

## Common Tasks

### Archive a Website

```bash
# Single URL
chronos archive https://web.archive.org/web/20090430060114/http://www.dar.org.br/

# Multiple URLs from file
chronos archive --input urls.txt

# With custom config
chronos archive --config my_config.yaml --input urls.txt
```

### Search Archived Content

```python
from chronos_archiver.indexing import ContentIndexer
from chronos_archiver.config import load_config

config = load_config()
indexer = ContentIndexer(config)

results = await indexer.search("search term")
```

### Run Background Workers

```bash
# Start workers
chronos workers start --count 8

# In another terminal, queue URLs
chronos archive --input large_list.txt
```

## Architecture Overview

```
┌────────────────────────────────────────────────────────────┐
│                    ChronosArchiver Pipeline                    │
│                                                                │
│  ┌──────────┐   ┌────────────┐   ┌─────────────────┐   ┌──────────┐  │
│  │ Discovery│──>│ Ingestion  │──>│ Transformation│──>│ Indexing │  │
│  │ (CDX API)│   │ (Download) │   │ (Transform)    │   │ (Store)  │  │
│  └──────────┘   └────────────┘   └─────────────────┘   └──────────┘  │
│       │            │                  │                │       │
│    [Queue 1]     [Queue 2]           [Queue 3]         [Database]  │
└────────────────────────────────────────────────────────────┘
```

For detailed architecture information, see [Architecture Guide](architecture.md).

## Support

- **Issues**: [GitHub Issues](https://github.com/dodopok/ChronosArchiver/issues)
- **Discussions**: [GitHub Discussions](https://github.com/dodopok/ChronosArchiver/discussions)
- **Email**: support@chronosarchiver.dev

## License

ChronosArchiver is licensed under the MIT License. See [LICENSE](../LICENSE) for details.

---

**Made with ❤️ by Douglas Araujo**