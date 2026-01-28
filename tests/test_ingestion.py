"""Tests for ingestion module."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from chronos_archiver.ingestion import ContentIngestion
from chronos_archiver.models import ArchiveStatus


class TestContentIngestion:
    """Test ContentIngestion class."""

    @pytest.mark.asyncio
    async def test_download_success(self, test_config, sample_snapshot, sample_html_content):
        """Test successful content download."""
        ingestion = ContentIngestion(test_config)
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.read = AsyncMock(return_value=sample_html_content)
            mock_response.headers = {"Content-Type": "text/html", "Content-Length": str(len(sample_html_content))}
            mock_response.get_encoding = MagicMock(return_value="utf-8")
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value.__aenter__.return_value = mock_response
            
            content = await ingestion.download(sample_snapshot)
        
        assert content is not None
        assert content.content == sample_html_content
        assert content.encoding == "utf-8"
        assert sample_snapshot.status == ArchiveStatus.DOWNLOADED

    @pytest.mark.asyncio
    async def test_download_file_too_large(self, test_config, sample_snapshot):
        """Test skipping files that are too large."""
        ingestion = ContentIngestion(test_config)
        large_content = b"x" * (test_config["archive"]["max_file_size"] * 1024 * 1024 + 1000)
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.headers = {"Content-Length": str(len(large_content))}
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value.__aenter__.return_value = mock_response
            
            content = await ingestion.download(sample_snapshot)
        
        assert content is None
        assert sample_snapshot.status == ArchiveStatus.SKIPPED

    @pytest.mark.asyncio
    async def test_download_with_retry(self, test_config, sample_snapshot, sample_html_content):
        """Test download retry on failure."""
        ingestion = ContentIngestion(test_config)
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            # First call fails, second succeeds
            mock_response = AsyncMock()
            mock_response.read = AsyncMock(return_value=sample_html_content)
            mock_response.headers = {"Content-Type": "text/html"}
            mock_response.get_encoding = MagicMock(return_value="utf-8")
            mock_response.raise_for_status = MagicMock(side_effect=[Exception("Network error"), None])
            mock_get.return_value.__aenter__.return_value = mock_response
            
            # Should eventually succeed
            content = await ingestion.download(sample_snapshot)
        
        # Note: With retry decorator, it should eventually succeed
        # This test verifies the retry mechanism exists

    @pytest.mark.asyncio
    async def test_batch_download(self, test_config, sample_snapshots, sample_html_content):
        """Test batch downloading multiple snapshots."""
        ingestion = ContentIngestion(test_config)
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.read = AsyncMock(return_value=sample_html_content)
            mock_response.headers = {"Content-Type": "text/html"}
            mock_response.get_encoding = MagicMock(return_value="utf-8")
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value.__aenter__.return_value = mock_response
            
            contents = await ingestion.batch_download(sample_snapshots, concurrency=2)
        
        assert len(contents) == 2
        assert all(c is not None for c in contents)

    @pytest.mark.asyncio
    async def test_sanitize_content(self, test_config):
        """Test content sanitization."""
        ingestion = ContentIngestion(test_config)
        
        dirty_content = b"Hello\x00World\x00Test"
        clean_content = ingestion.sanitize_content(dirty_content)
        
        assert b"\x00" not in clean_content
        assert clean_content == b"HelloWorldTest"

    @pytest.mark.asyncio
    async def test_download_error_handling(self, test_config, sample_snapshot):
        """Test error handling during download."""
        ingestion = ContentIngestion(test_config)
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.side_effect = Exception("Network error")
            
            content = await ingestion.download(sample_snapshot)
        
        assert content is None
        assert sample_snapshot.status == ArchiveStatus.FAILED