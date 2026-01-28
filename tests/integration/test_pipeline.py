"""Integration tests for the complete pipeline."""

import pytest
import shutil
from pathlib import Path
from chronos_archiver import ChronosArchiver
from chronos_archiver.discovery import WaybackDiscovery
from chronos_archiver.ingestion import ContentIngestion
from chronos_archiver.transformation import ContentTransformation
from chronos_archiver.indexing import ContentIndexer
from chronos_archiver.models import ArchiveStatus
from unittest.mock import patch, AsyncMock, MagicMock


class TestPipelineIntegration:
    """Test the complete 4-stage pipeline."""

    @pytest.mark.asyncio
    async def test_complete_pipeline(self, test_config, sample_snapshot, sample_html_content, cdx_api_response):
        """Test complete pipeline from discovery to indexing."""
        # Mock external calls
        with patch('aiohttp.ClientSession.get') as mock_get:
            # Mock CDX API response
            mock_cdx_response = AsyncMock()
            mock_cdx_response.json = AsyncMock(return_value=cdx_api_response)
            mock_cdx_response.raise_for_status = MagicMock()
            
            # Mock content download
            mock_content_response = AsyncMock()
            mock_content_response.read = AsyncMock(return_value=sample_html_content)
            mock_content_response.headers = {"Content-Type": "text/html"}
            mock_content_response.get_encoding = MagicMock(return_value="utf-8")
            mock_content_response.raise_for_status = MagicMock()
            
            # Alternate between CDX and content responses
            mock_get.return_value.__aenter__.side_effect = [
                mock_cdx_response,
                mock_content_response,
            ]
            
            try:
                # Stage 1: Discovery
                discovery = WaybackDiscovery(test_config)
                snapshots = await discovery.find_snapshots("http://www.dar.org.br/")
                assert len(snapshots) > 0
                snapshot = snapshots[0]
                
                # Stage 2: Ingestion
                ingestion = ContentIngestion(test_config)
                downloaded = await ingestion.download(snapshot)
                assert downloaded is not None
                assert snapshot.status == ArchiveStatus.DOWNLOADED
                
                # Stage 3: Transformation
                transformation = ContentTransformation(test_config)
                transformed = await transformation.transform(downloaded)
                assert transformed is not None
                assert snapshot.status == ArchiveStatus.TRANSFORMED
                
                # Stage 4: Indexing
                indexer = ContentIndexer(test_config)
                indexed = await indexer.index(transformed)
                assert indexed is not None
                assert snapshot.status == ArchiveStatus.INDEXED
                
                # Verify search works
                results = await indexer.search("Diocese")
                assert len(results) > 0
                
                await indexer.close()
            finally:
                # Cleanup
                if Path(test_config["archive"]["output_dir"]).exists():
                    shutil.rmtree(test_config["archive"]["output_dir"])

    @pytest.mark.asyncio
    async def test_pipeline_error_handling(self, test_config, sample_snapshot):
        """Test pipeline error handling."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.side_effect = Exception("Network error")
            
            ingestion = ContentIngestion(test_config)
            downloaded = await ingestion.download(sample_snapshot)
            
            assert downloaded is None
            assert sample_snapshot.status == ArchiveStatus.FAILED

    @pytest.mark.asyncio
    async def test_batch_processing(self, test_config, sample_snapshots, sample_html_content):
        """Test batch processing through pipeline."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.read = AsyncMock(return_value=sample_html_content)
            mock_response.headers = {"Content-Type": "text/html"}
            mock_response.get_encoding = MagicMock(return_value="utf-8")
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value.__aenter__.return_value = mock_response
            
            try:
                ingestion = ContentIngestion(test_config)
                contents = await ingestion.batch_download(sample_snapshots)
                
                assert len(contents) == len(sample_snapshots)
                assert all(c is not None for c in contents)
                
                # Transform all
                transformation = ContentTransformation(test_config)
                transformed_list = []
                for content in contents:
                    if content:
                        transformed = await transformation.transform(content)
                        if transformed:
                            transformed_list.append(transformed)
                
                assert len(transformed_list) > 0
                
                # Index all
                indexer = ContentIndexer(test_config)
                for transformed in transformed_list:
                    indexed = await indexer.index(transformed)
                    assert indexed is not None
                
                await indexer.close()
            finally:
                if Path(test_config["archive"]["output_dir"]).exists():
                    shutil.rmtree(test_config["archive"]["output_dir"])