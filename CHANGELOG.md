# Changelog

All notable changes to ChronosArchiver will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-01-28

### Added

#### Core Features
- Four-stage archival pipeline:
  - Discovery: CDX API integration for finding URLs
  - Ingestion: Async content downloading with retry logic
  - Transformation: Link rewriting and metadata extraction
  - Indexing: Storage and full-text search
- Asynchronous processing with message queues (Redis)
- Configuration management with YAML and Pydantic validation
- CLI interface with Click
- Comprehensive data models with Pydantic

#### Discovery Module
- CDX API client for Wayback Machine
- Support for both Wayback URLs and original URLs
- Snapshot filtering by status code
- Deduplication by content digest
- Batch discovery for multiple URLs

#### Ingestion Module
- Async HTTP client with aiohttp
- Rate limiting and throttling
- Automatic retries with exponential backoff
- Content validation and sanitization
- File size limits
- Content hash verification

#### Transformation Module
- HTML parsing with BeautifulSoup and lxml
- Link rewriting for local archival:
  - Relative to absolute conversion
  - Wayback timestamp prefixing
  - CSS url() rewriting
- Metadata extraction:
  - Title, description, keywords
  - Open Graph tags
  - Language detection
- Plain text extraction for search
- Link extraction
- Optional script and comment removal

#### Indexing Module
- File storage with date-based organization (YYYY/MM/DD)
- Optional gzip compression
- SQLite and PostgreSQL support
- Full-text search capabilities
- Metadata indexing with SQLAlchemy

#### Queue Management
- Redis-backed message queues
- Worker pool management
- Message retry logic
- Graceful shutdown handling

#### CLI Commands
- `chronos archive`: Archive URLs
- `chronos workers start`: Start background workers
- `chronos init`: Initialize project structure
- `chronos validate-config`: Validate configuration

#### Testing
- Comprehensive unit tests for all modules
- Integration tests for pipeline
- Test fixtures with sample data
- Mock external services for offline testing
- pytest configuration with async support
- Code coverage reporting

#### Documentation
- Comprehensive README with examples
- Architecture documentation
- API reference
- Usage guide
- Contributing guidelines
- Sample sites for testing

#### DevOps
- Dockerfile for containerization
- docker-compose.yml for multi-service deployment
- GitHub Actions CI/CD pipeline:
  - Multi-OS testing (Linux, macOS, Windows)
  - Multi-Python version testing (3.8-3.12)
  - Linting (flake8, black, isort, mypy)
  - Code coverage with Codecov
  - Docker image building
  - Integration testing
- Release automation workflow

#### Examples
- Basic usage examples
- Advanced usage examples
- Sample URLs for testing

### Dependencies

#### Core
- aiohttp >= 3.8.0 - Async HTTP client
- asyncio-throttle >= 1.0.0 - Rate limiting
- beautifulsoup4 >= 4.11.0 - HTML parsing
- click >= 8.0.0 - CLI framework
- lxml >= 4.9.0 - XML/HTML parser
- pydantic >= 2.0.0 - Data validation
- PyYAML >= 6.0 - Configuration parsing
- redis >= 4.5.0 - Queue backend
- requests >= 2.28.0 - HTTP library
- SQLAlchemy >= 2.0.0 - ORM
- tqdm >= 4.65.0 - Progress bars

#### Development
- black >= 23.0.0 - Code formatting
- flake8 >= 6.0.0 - Linting
- isort >= 5.12.0 - Import sorting
- mypy >= 1.0.0 - Type checking
- pytest >= 7.0.0 - Testing framework
- pytest-asyncio >= 0.21.0 - Async test support
- pytest-cov >= 4.0.0 - Coverage reporting
- pytest-mock >= 3.10.0 - Mocking

### Project Structure

```
ChronosArchiver/
├── src/chronos_archiver/     # Source code
├── tests/                   # Test suite
├── docs/                    # Documentation
├── examples/                # Usage examples
├── .github/workflows/       # CI/CD pipelines
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Multi-container setup
├── pyproject.toml          # Modern Python packaging
├── setup.py                # Package setup
├── requirements.txt        # Dependencies
├── requirements-dev.txt    # Dev dependencies
├── config.yaml.example     # Sample configuration
└── README.md               # Project documentation
```

### Sample Sites Included

- Diocese Anglicana do Recife (DAR):
  - 2009-04-30 snapshot
  - 2012-03-02 snapshot
  - 2015-04-06 snapshot
  - 2010-12-23 snapshot (dar.ieab.org.br)

- Igreja Episcopal Anglicana do Brasil (IEAB):
  - 2004-10-22 snapshot (ieabrecife.com.br)
  - 2005-08-29 snapshot (ieabweb.org.br)
  - 2005-11-25 snapshot (ieabweb.org.br/dar/)

## [Unreleased]

### Planned Features

- WARC format export
- Incremental archiving (only new snapshots)
- Web UI for browsing archived content
- Elasticsearch integration for advanced search
- Webhook notifications
- RESTful API
- Additional archive sources beyond Wayback Machine
- Kubernetes deployment manifests
- Multi-region distribution
- Progress monitoring dashboard

---

**Note**: This is the initial release of ChronosArchiver. Future releases will follow semantic versioning:
- MAJOR version for incompatible API changes
- MINOR version for backwards-compatible functionality
- PATCH version for backwards-compatible bug fixes