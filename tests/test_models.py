"""Tests for data models."""

import pytest
from datetime import datetime
from chronos_archiver.models import (
    ArchiveSnapshot,
    ArchiveStatus,
    DownloadedContent,
    TransformedContent,
    IndexedContent,
    QueueMessage,
    ProcessingStats,
)


class TestModels:
    """Test data models."""

    def test_archive_snapshot_creation(self):
        """Test creating an ArchiveSnapshot."""
        snapshot = ArchiveSnapshot(
            url="https://web.archive.org/web/20090430060114/http://www.dar.org.br/",
            original_url="http://www.dar.org.br/",
            timestamp="20090430060114",
        )
        
        assert snapshot.url is not None
        assert snapshot.status == ArchiveStatus.DISCOVERED
        assert isinstance(snapshot.created_at, datetime)

    def test_downloaded_content_creation(self, sample_snapshot, sample_html_content):
        """Test creating DownloadedContent."""
        downloaded = DownloadedContent(
            snapshot=sample_snapshot,
            content=sample_html_content,
            headers={"Content-Type": "text/html"},
        )
        
        assert downloaded.snapshot == sample_snapshot
        assert downloaded.content == sample_html_content
        assert isinstance(downloaded.downloaded_at, datetime)

    def test_transformed_content_creation(self, sample_snapshot):
        """Test creating TransformedContent."""
        transformed = TransformedContent(
            snapshot=sample_snapshot,
            content="<html>Transformed</html>",
            metadata={"title": "Test"},
        )
        
        assert transformed.content is not None
        assert transformed.metadata["title"] == "Test"
        assert isinstance(transformed.transformed_at, datetime)

    def test_queue_message_creation(self):
        """Test creating QueueMessage."""
        message = QueueMessage(
            id="test-123",
            type="snapshot",
            payload={"url": "http://example.com"},
        )
        
        assert message.id == "test-123"
        assert message.retry_count == 0
        assert isinstance(message.created_at, datetime)

    def test_processing_stats(self):
        """Test ProcessingStats model."""
        stats = ProcessingStats(
            total_snapshots=100,
            discovered=100,
            downloaded=90,
            transformed=85,
            indexed=80,
            failed=5,
        )
        
        assert stats.success_rate == 80.0
        assert stats.duration is None  # No end time set
        
        stats.end_time = datetime.utcnow()
        assert stats.duration is not None
        assert stats.duration >= 0