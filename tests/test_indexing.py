"""Tests for indexing module."""

import pytest
from chronos_archiver.indexing import ContentIndexer
from chronos_archiver.models import ArchiveSnapshot, TransformedContent


@pytest.mark.asyncio
async def test_index_content(tmp_path):
    """Test content indexing."""
    config = {
        "archive": {"output_dir": str(tmp_path)},
        "database": {"type": "sqlite", "sqlite_path": str(tmp_path / "test.db")},
        "indexing": {"compress_content": False},
    }

    indexer = ContentIndexer(config)

    snapshot = ArchiveSnapshot(
        url="https://web.archive.org/web/20090430060114/http://www.dar.org.br/",
        original_url="http://www.dar.org.br/",
        timestamp="20090430060114",
    )

    transformed = TransformedContent(
        snapshot=snapshot,
        content="<html><body>Test</body></html>",
        text_content="Test",
        metadata={"title": "Test Page"},
        links=[],
    )

    indexed = await indexer.index(transformed)

    assert indexed is not None
    assert indexed.id is not None
    assert indexed.metadata["title"] == "Test Page"

    await indexer.close()


@pytest.mark.asyncio
async def test_search(tmp_path):
    """Test content search."""
    config = {
        "archive": {"output_dir": str(tmp_path)},
        "database": {"type": "sqlite", "sqlite_path": str(tmp_path / "test.db")},
    }

    indexer = ContentIndexer(config)

    # Index some content first
    snapshot = ArchiveSnapshot(
        url="https://web.archive.org/web/20090430060114/http://www.dar.org.br/",
        original_url="http://www.dar.org.br/",
        timestamp="20090430060114",
    )

    transformed = TransformedContent(
        snapshot=snapshot,
        content="<html><body>Test</body></html>",
        text_content="Test searchable content",
        metadata={"title": "Searchable Page"},
        links=[],
    )

    await indexer.index(transformed)

    # Search
    results = await indexer.search("searchable")

    assert len(results) > 0

    await indexer.close()