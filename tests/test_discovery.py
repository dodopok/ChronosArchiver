"""Tests for discovery module."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from chronos_archiver.discovery import WaybackDiscovery
from chronos_archiver.models import ArchiveStatus


class TestWaybackDiscovery:
    """Test WaybackDiscovery class."""

    @pytest.mark.asyncio
    async def test_find_snapshots_single_wayback_url(self, test_config, sample_snapshot):
        """Test finding a single snapshot from Wayback URL."""
        discovery = WaybackDiscovery(test_config)
        url = "https://web.archive.org/web/20090430060114/http://www.dar.org.br/"
        
        snapshots = await discovery.find_snapshots(url)
        
        assert len(snapshots) == 1
        assert snapshots[0].url == url
        assert snapshots[0].original_url == "http://www.dar.org.br/"
        assert snapshots[0].timestamp == "20090430060114"
        assert snapshots[0].status == ArchiveStatus.DISCOVERED

    @pytest.mark.asyncio
    async def test_find_snapshots_via_cdx_api(self, test_config, cdx_api_response):
        """Test finding snapshots via CDX API."""
        discovery = WaybackDiscovery(test_config)
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.json = AsyncMock(return_value=cdx_api_response)
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value.__aenter__.return_value = mock_response
            
            snapshots = await discovery.find_snapshots("http://www.dar.org.br/")
        
        assert len(snapshots) == 3
        assert snapshots[0].timestamp == "20090430060114"
        assert snapshots[1].timestamp == "20120302052501"
        assert snapshots[2].timestamp == "20150406103050"

    @pytest.mark.asyncio
    async def test_parse_cdx_response(self, test_config, cdx_api_response):
        """Test CDX response parsing."""
        discovery = WaybackDiscovery(test_config)
        
        snapshots = discovery._parse_cdx_response(cdx_api_response)
        
        assert len(snapshots) == 3
        assert all(s.status_code == 200 for s in snapshots)
        assert all(s.mime_type == "text/html" for s in snapshots)

    @pytest.mark.asyncio
    async def test_filter_by_status_code(self, test_config):
        """Test filtering snapshots by status code."""
        discovery = WaybackDiscovery(test_config)
        test_config["discovery"]["filter_status_codes"] = [200]
        
        cdx_data = [
            ["timestamp", "original", "mimetype", "statuscode", "digest", "length"],
            ["20090430060114", "http://www.dar.org.br/", "text/html", "200", "ABC123", "5000"],
            ["20100430060114", "http://www.dar.org.br/", "text/html", "404", "DEF456", "1000"],
            ["20110430060114", "http://www.dar.org.br/", "text/html", "301", "GHI789", "2000"],
        ]
        
        snapshots = discovery._parse_cdx_response(cdx_data)
        
        # Should only get the 200 status
        assert len(snapshots) == 1
        assert snapshots[0].status_code == 200

    @pytest.mark.asyncio
    async def test_deduplicate_snapshots(self, test_config):
        """Test deduplication of snapshots by digest."""
        discovery = WaybackDiscovery(test_config)
        
        cdx_data = [
            ["timestamp", "original", "mimetype", "statuscode", "digest", "length"],
            ["20090430060114", "http://www.dar.org.br/", "text/html", "200", "ABC123", "5000"],
            ["20100430060114", "http://www.dar.org.br/", "text/html", "200", "ABC123", "5000"],  # Duplicate
            ["20110430060114", "http://www.dar.org.br/", "text/html", "200", "DEF456", "6000"],
        ]
        
        snapshots = discovery._parse_cdx_response(cdx_data)
        
        # Should only get 2 unique snapshots
        assert len(snapshots) == 2
        assert snapshots[0].digest == "ABC123"
        assert snapshots[1].digest == "DEF456"

    @pytest.mark.asyncio
    async def test_batch_discover(self, test_config, cdx_api_response):
        """Test batch discovery of multiple URLs."""
        discovery = WaybackDiscovery(test_config)
        urls = [
            "https://web.archive.org/web/20090430060114/http://www.dar.org.br/",
            "https://web.archive.org/web/20120302052501/http://www.dar.org.br/",
        ]
        
        snapshots = await discovery.batch_discover(urls)
        
        assert len(snapshots) == 2
        assert all(s.status == ArchiveStatus.DISCOVERED for s in snapshots)

    @pytest.mark.asyncio
    async def test_cdx_api_error_handling(self, test_config):
        """Test error handling when CDX API fails."""
        discovery = WaybackDiscovery(test_config)
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.side_effect = Exception("API Error")
            
            snapshots = await discovery.find_snapshots("http://www.dar.org.br/")
        
        assert len(snapshots) == 0