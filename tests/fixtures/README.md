# Test Fixtures

This directory contains test fixtures for ChronosArchiver.

## Files

### sample_cdx_response.json
Sample CDX API response containing metadata for archived snapshots of DAR and IEAB websites.

### sample_html_dar.html
Sample HTML content from the Diocese Anglicana do Recife website (2009 snapshot).

### sample_html_ieab.html
Sample HTML content from the Igreja Episcopal Anglicana do Brasil website.

### sample_sites.txt
List of sample Wayback Machine URLs used for testing, including:
- DAR website snapshots from 2009, 2012, and 2015
- IEAB website snapshots from 2004-2005

## Usage

These fixtures are used in unit and integration tests to mock external API responses and provide consistent test data without requiring actual network requests to the Wayback Machine.

Example:
```python
import json
from pathlib import Path

# Load CDX response fixture
fixtures_dir = Path(__file__).parent / "fixtures"
with open(fixtures_dir / "sample_cdx_response.json") as f:
    cdx_data = json.load(f)
```