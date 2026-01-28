# ChronosArchiver Examples

This directory contains example scripts demonstrating various use cases of ChronosArchiver.

## Files

### basic_usage.py
Basic examples covering:
- Archiving a single URL
- Archiving multiple URLs
- Discovering and archiving all snapshots for a site
- Searching archived content

**Run:**
```bash
python examples/basic_usage.py
```

### advanced_usage.py
Advanced examples covering:
- Batch archiving with progress tracking
- Custom transformation settings
- Parallel processing with multiple workers
- Filtered discovery
- Export functionality

**Run:**
```bash
python examples/advanced_usage.py
```

### sample_sites.txt
List of sample Wayback Machine URLs for testing, including:
- Diocese Anglicana do Recife (DAR) snapshots from 2009-2015
- Igreja Episcopal Anglicana do Brasil (IEAB) snapshots from 2004-2005

**Usage:**
```bash
chronos archive --input examples/sample_sites.txt
```

## Prerequisites

Before running the examples:

1. **Install ChronosArchiver:**
   ```bash
   pip install -e .
   ```

2. **Start Redis:**
   ```bash
   redis-server
   ```
   
   Or using Docker:
   ```bash
   docker run -d -p 6379:6379 redis:7-alpine
   ```

3. **Configure (optional):**
   ```bash
   cp config.yaml.example config.yaml
   # Edit config.yaml with your settings
   ```

## Quick Start

### Archive a Single URL
```bash
chronos archive https://web.archive.org/web/20090430060114/http://www.dar.org.br/
```

### Archive from File
```bash
chronos archive --input examples/sample_sites.txt --workers 4
```

### Start Background Workers
```bash
chronos workers start --count 4
```

## Example Output

After running the examples, you'll find:

```
archive/
├── content/
│   └── 2009/
│       └── 04/
│           └── 30/
│               └── 20090430060114_www.dar.org.br_.html
└── chronos.db
```

## Troubleshooting

### Redis Connection Error
Ensure Redis is running:
```bash
redis-cli ping
# Should return: PONG
```

### Import Errors
Make sure ChronosArchiver is installed:
```bash
pip install -e .
```

### Rate Limiting
If you encounter rate limiting from the Wayback Machine, adjust settings in `config.yaml`:
```yaml
processing:
  requests_per_second: 2  # Lower this value
  retry_delay: 10  # Increase delay
```

## Additional Resources

- [Main Documentation](../README.md)
- [API Reference](../docs/api.md)
- [Architecture Guide](../docs/architecture.md)
- [Contributing Guidelines](../CONTRIBUTING.md)