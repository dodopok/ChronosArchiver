"""Pytest configuration and fixtures."""

import json
import pytest
from pathlib import Path
from datetime import datetime
from chronos_archiver.models import ArchiveSnapshot, ArchiveStatus, DownloadedContent, TransformedContent


@pytest.fixture
def test_config():
    """Test configuration."""
    return {
        "archive": {
            "output_dir": "./test_archive",
            "user_agent": "ChronosArchiver-Test/1.0",
            "max_file_size": 10,
        },
        "queue": {
            "backend": "redis",
            "redis_url": "redis://localhost:6379/15",
        },
        "processing": {
            "workers": 2,
            "batch_size": 5,
            "retry_attempts": 2,
            "requests_per_second": 10,
        },
        "database": {
            "type": "sqlite",
            "sqlite_path": "./test_archive/test.db",
        },
        "discovery": {
            "cdx_api_url": "https://web.archive.org/cdx/search/cdx",
            "filter_status_codes": [200],
            "deduplicate_snapshots": True,
        },
        "ingestion": {
            "wayback_url": "https://web.archive.org/web",
            "verify_ssl": True,
        },
        "transformation": {
            "rewrite_links": True,
            "extract_metadata": True,
        },
        "indexing": {
            "compress_content": False,
        },
    }


@pytest.fixture
def sample_snapshot():
    """Sample archive snapshot."""
    return ArchiveSnapshot(
        url="https://web.archive.org/web/20090430060114/http://www.dar.org.br/",
        original_url="http://www.dar.org.br/",
        timestamp="20090430060114",
        mime_type="text/html",
        status_code=200,
        digest="ABC123DEF456",
        length=5000,
        status=ArchiveStatus.DISCOVERED,
    )


@pytest.fixture
def sample_snapshots():
    """Multiple sample snapshots."""
    return [
        ArchiveSnapshot(
            url="https://web.archive.org/web/20090430060114/http://www.dar.org.br/",
            original_url="http://www.dar.org.br/",
            timestamp="20090430060114",
            mime_type="text/html",
            status_code=200,
            digest="ABC123",
        ),
        ArchiveSnapshot(
            url="https://web.archive.org/web/20120302052501/http://www.dar.org.br/",
            original_url="http://www.dar.org.br/",
            timestamp="20120302052501",
            mime_type="text/html",
            status_code=200,
            digest="DEF456",
        ),
    ]


@pytest.fixture
def sample_html_content():
    """Sample HTML content."""
    return b'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="description" content="Diocese Anglicana do Recife">
    <title>DAR - Diocese Anglicana do Recife</title>
    <link rel="stylesheet" href="/css/style.css">
</head>
<body>
    <header>
        <h1>Diocese Anglicana do Recife</h1>
    </header>
    <nav>
        <a href="/sobre">Sobre</a>
        <a href="/noticias">Notícias</a>
        <a href="http://www.ieab.org.br/">IEAB</a>
    </nav>
    <main>
        <article>
            <h2>Bem-vindo à DAR</h2>
            <p>A Diocese Anglicana do Recife serve a região nordeste do Brasil.</p>
            <img src="/images/logo.png" alt="Logo DAR">
        </article>
    </main>
    <script src="/js/main.js"></script>
</body>
</html>'''


@pytest.fixture
def sample_downloaded_content(sample_snapshot, sample_html_content):
    """Sample downloaded content."""
    return DownloadedContent(
        snapshot=sample_snapshot,
        content=sample_html_content,
        headers={"Content-Type": "text/html; charset=utf-8"},
        encoding="utf-8",
    )


@pytest.fixture
def sample_transformed_content(sample_snapshot):
    """Sample transformed content."""
    transformed_html = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="utf-8"/>
    <meta content="Diocese Anglicana do Recife" name="description"/>
    <title>DAR - Diocese Anglicana do Recife</title>
    <link href="/20090430060114/http://www.dar.org.br/css/style.css" rel="stylesheet"/>
</head>
<body>
    <header>
        <h1>Diocese Anglicana do Recife</h1>
    </header>
    <nav>
        <a href="/20090430060114/http://www.dar.org.br/sobre">Sobre</a>
        <a href="/20090430060114/http://www.dar.org.br/noticias">Notícias</a>
        <a href="/20090430060114/http://www.ieab.org.br/">IEAB</a>
    </nav>
    <main>
        <article>
            <h2>Bem-vindo à DAR</h2>
            <p>A Diocese Anglicana do Recife serve a região nordeste do Brasil.</p>
            <img alt="Logo DAR" src="/20090430060114/http://www.dar.org.br/images/logo.png"/>
        </article>
    </main>
</body>
</html>'''
    
    return TransformedContent(
        snapshot=sample_snapshot,
        content=transformed_html,
        text_content="Diocese Anglicana do Recife Sobre Notícias IEAB Bem-vindo à DAR A Diocese Anglicana do Recife serve a região nordeste do Brasil.",
        metadata={
            "title": "DAR - Diocese Anglicana do Recife",
            "description": "Diocese Anglicana do Recife",
            "language": "pt-BR",
        },
        links=[
            "/20090430060114/http://www.dar.org.br/css/style.css",
            "/20090430060114/http://www.dar.org.br/sobre",
            "/20090430060114/http://www.dar.org.br/noticias",
            "/20090430060114/http://www.ieab.org.br/",
            "/20090430060114/http://www.dar.org.br/images/logo.png",
        ],
    )


@pytest.fixture
def cdx_api_response():
    """Mock CDX API response."""
    return [
        ["timestamp", "original", "mimetype", "statuscode", "digest", "length"],
        ["20090430060114", "http://www.dar.org.br/", "text/html", "200", "ABC123DEF456", "5000"],
        ["20120302052501", "http://www.dar.org.br/", "text/html", "200", "GHI789JKL012", "6500"],
        ["20150406103050", "http://dar.org.br/", "text/html", "200", "MNO345PQR678", "7200"],
    ]


@pytest.fixture
def fixtures_dir():
    """Path to fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture(scope="function")
async def cleanup_test_files():
    """Cleanup test files after test."""
    yield
    # Cleanup code here
    import shutil
    test_dirs = ["./test_archive", "./archive"]
    for dir_path in test_dirs:
        if Path(dir_path).exists():
            shutil.rmtree(dir_path)