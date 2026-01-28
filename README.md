# ChronosArchiver

> An archival system to download and preserve websites from the Internet Archive's Wayback Machine

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## Overview

ChronosArchiver is a robust, production-ready system for downloading, transforming, and preserving archived websites from the Internet Archive's Wayback Machine. It implements a 4-stage asynchronous pipeline designed to handle large-scale archival operations efficiently.

## Architecture

The system is built around a 4-stage pipeline:

```
┌───────────┐     ┌────────────┐     ┌──────────────────┐     ┌──────────┐
│ Discovery │ --> │ Ingestion  │ --> │ Transformation   │ --> │ Indexing │
│  (CDX API)│     │ (Download) │     │ (Link Rewriting) │     │ (Storage)│
└───────────┘     └────────────┘     └──────────────────┘     └──────────┘
       ↓                ↓                     ↓                      ↓
   [Queue 1]        [Queue 2]             [Queue 3]            [Database]
```

### Stage 1: Discovery
- Queries the Wayback Machine CDX API to find all captured URLs
- Identifies snapshots, timestamps, and MIME types
- Filters and validates URLs for processing
- Outputs: URL metadata to ingestion queue

### Stage 2: Ingestion
- Downloads content from Wayback Machine
- Sanitizes and validates downloaded data
- Handles retries and error recovery
- Outputs: Raw content to transformation queue

### Stage 3: Transformation
- Rewrites links to point to local archived versions
- Extracts metadata (titles, dates, authors)
- Normalizes HTML/CSS structure
- Outputs: Transformed content to indexing queue

### Stage 4: Indexing
- Stores content in structured format
- Creates searchable index
- Maintains URL mappings and relationships
- Outputs: Searchable archive database

## Features

- ✅ **Asynchronous Processing**: Built with `asyncio` and `aiohttp` for high performance
- ✅ **Message Queue System**: Redis/RabbitMQ integration for distributed processing
- ✅ **Configurable Pipeline**: YAML-based configuration for all stages
- ✅ **Robust Error Handling**: Automatic retries, logging, and failure recovery
- ✅ **CLI Interface**: Easy-to-use command-line tools
- ✅ **Extensible Design**: Plugin architecture for custom processors
- ✅ **Comprehensive Testing**: Unit and integration tests included
- ✅ **Production Ready**: Logging, monitoring, and deployment support

## Installation

### Prerequisites

- Python 3.8 or higher
- Redis (for queue management)
- SQLite/PostgreSQL (for indexing)

### Basic Installation

```bash
# Clone the repository
git clone https://github.com/dodopok/ChronosArchiver.git
cd ChronosArchiver

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Production Installation

```bash
pip install chronos-archiver
```

## Quick Start

### 1. Configure the System

Create a `config.yaml` file (or copy from `config.yaml.example`):

```yaml
archive:
  output_dir: "./archive"
  user_agent: "ChronosArchiver/1.0"
  
queue:
  backend: "redis"
  redis_url: "redis://localhost:6379"
  
processing:
  workers: 4
  batch_size: 10
  retry_attempts: 3
```

### 2. Basic Usage

```bash
# Archive a single URL
chronos archive https://web.archive.org/web/20090430060114/http://www.dar.org.br/

# Archive from a list of URLs
chronos archive --input examples/sample_sites.txt

# Run with specific configuration
chronos archive --config config.yaml --input urls.txt

# Start processing workers
chronos workers start --count 4
```

### 3. Programmatic Usage

```python
from chronos_archiver import ChronosArchiver
from chronos_archiver.config import load_config

# Initialize archiver
config = load_config('config.yaml')
archiver = ChronosArchiver(config)

# Archive a URL
await archiver.archive_url(
    'https://web.archive.org/web/20090430060114/http://www.dar.org.br/'
)

# Archive multiple URLs
urls = [
    'https://web.archive.org/web/20120302052501/http://www.dar.org.br/',
    'https://web.archive.org/web/20150406103050/http://dar.org.br/',
]
await archiver.archive_urls(urls)
```

## Sample Sites

The project includes example URLs for testing:

```python
# DAR (Diocese Anglicana do Recife) historical snapshots
- https://web.archive.org/web/20090430060114/http://www.dar.org.br/
- https://web.archive.org/web/20120302052501/http://www.dar.org.br/
- https://web.archive.org/web/20150406103050/http://dar.org.br/
- https://web.archive.org/web/20101223085644/http://dar.ieab.org.br/

# IEAB (Igreja Episcopal Anglicana do Brasil) historical snapshots
- https://web.archive.org/web/20041022131803fw_/http://www.ieabrecife.com.br/
- https://web.archive.org/web/20050829171410fw_/http://www.ieabweb.org.br/
- https://web.archive.org/web/20051125104316fw_/http://www.ieabweb.org.br/dar/
```

See `examples/sample_sites.txt` for the complete list.

## Project Structure

```
ChronosArchiver/
├── src/
│   └── chronos_archiver/
│       ├── __init__.py          # Package initialization
│       ├── __main__.py          # CLI entry point
│       ├── cli.py               # Command-line interface
│       ├── config.py            # Configuration management
│       ├── discovery.py         # Stage 1: URL discovery
│       ├── ingestion.py         # Stage 2: Content download
│       ├── transformation.py    # Stage 3: Content transformation
│       ├── indexing.py          # Stage 4: Storage & indexing
│       ├── queue_manager.py     # Async queue management
│       ├── models.py            # Data models
│       └── utils.py             # Utility functions
├── tests/
│   ├── test_discovery.py
│   ├── test_ingestion.py
│   ├── test_transformation.py
│   └── test_indexing.py
├── docs/
│   ├── architecture.md          # Detailed architecture docs
│   ├── api.md                   # API reference
│   └── usage.md                 # Usage guide
├── examples/
│   ├── sample_sites.txt         # Example URLs
│   ├── basic_usage.py           # Basic examples
│   └── advanced_usage.py        # Advanced examples
├── config.yaml.example          # Sample configuration
├── requirements.txt             # Dependencies
├── requirements-dev.txt         # Development dependencies
├── setup.py                     # Package setup
├── pyproject.toml               # Modern Python packaging
├── CONTRIBUTING.md              # Contribution guidelines
└── README.md                    # This file
```

## Documentation

- **[Architecture Guide](docs/architecture.md)**: Detailed system design and component interactions
- **[API Reference](docs/api.md)**: Complete API documentation
- **[Usage Guide](docs/usage.md)**: Advanced usage patterns and examples
- **[Contributing](CONTRIBUTING.md)**: How to contribute to the project

## Development

### Setup Development Environment

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Run tests with coverage
pytest --cov=chronos_archiver tests/

# Format code
black src/ tests/
isort src/ tests/

# Lint code
flake8 src/ tests/
mypy src/
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_discovery.py

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=chronos_archiver --cov-report=html
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Roadmap

- [ ] Add support for parallel processing across multiple machines
- [ ] Implement incremental archiving (only download new snapshots)
- [ ] Add web UI for browsing archived content
- [ ] Support for additional archive sources beyond Wayback Machine
- [ ] Advanced search with full-text indexing
- [ ] Export to WARC format
- [ ] Docker containerization
- [ ] Kubernetes deployment manifests

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Internet Archive](https://archive.org/) for providing the Wayback Machine
- The Python community for excellent async libraries
- Contributors and maintainers

## Support

- 📧 Email: support@chronosarchiver.dev
- 🐛 Issues: [GitHub Issues](https://github.com/dodopok/ChronosArchiver/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/dodopok/ChronosArchiver/discussions)

---

**Made with ❤️ by Douglas Araujo**