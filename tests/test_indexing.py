"""Tests for indexing module."""

import pytest
import shutil
from pathlib import Path
from chronos_archiver.indexing import ContentIndexer
from chronos_archiver.models import ArchiveStatus


class TestContentIndexer:
    """Test ContentIndexer class."""

    @pytest.mark.asyncio
    async def test_index_success(self, test_config, sample_transformed_content):
        """Test successful content indexing."""
        indexer = ContentIndexer(test_config)
        
        try:
            indexed = await indexer.index(sample_transformed_content)
            
            assert indexed is not None
            assert indexed.id is not None
            assert sample_transformed_content.snapshot.status == ArchiveStatus.INDEXED
        finally:
            await indexer.close()
            # Cleanup
            if Path(test_config["archive"]["output_dir"]).exists():
                shutil.rmtree(test_config["archive"]["output_dir"])

    @pytest.mark.asyncio
    async def test_content_storage(self, test_config, sample_transformed_content):
        """Test that content is stored to filesystem."""
        indexer = ContentIndexer(test_config)
        
        try:
            indexed = await indexer.index(sample_transformed_content)
            
            # Check that file was created
            output_dir = Path(test_config["archive"]["output_dir"])
            content_files = list(output_dir.glob("content/**/*.html"))
            assert len(content_files) > 0
        finally:
            await indexer.close()
            if Path(test_config["archive"]["output_dir"]).exists():
                shutil.rmtree(test_config["archive"]["output_dir"])

    @pytest.mark.asyncio
    async def test_database_storage(self, test_config, sample_transformed_content):
        """Test that metadata is stored in database."""
        indexer = ContentIndexer(test_config)
        
        try:
            indexed = await indexer.index(sample_transformed_content)
            
            # Verify database entry
            assert indexed.id is not None
            assert indexed.snapshot.url == sample_transformed_content.snapshot.url
        finally:
            await indexer.close()
            if Path(test_config["archive"]["output_dir"]).exists():
                shutil.rmtree(test_config["archive"]["output_dir"])

    @pytest.mark.asyncio
    async def test_search_functionality(self, test_config, sample_transformed_content):
        """Test search functionality."""
        indexer = ContentIndexer(test_config)
        
        try:
            # Index content first
            await indexer.index(sample_transformed_content)
            
            # Search for it
            results = await indexer.search("Diocese Anglicana")
            
            assert len(results) > 0
            assert "Diocese" in results[0].text_content or "Anglicana" in results[0].text_content
        finally:
            await indexer.close()
            if Path(test_config["archive"]["output_dir"]).exists():
                shutil.rmtree(test_config["archive"]["output_dir"])

    @pytest.mark.asyncio
    async def test_compression(self, test_config, sample_transformed_content):
        """Test content compression."""
        test_config["indexing"]["compress_content"] = True
        indexer = ContentIndexer(test_config)
        
        try:
            await indexer.index(sample_transformed_content)
            
            # Check for compressed file
            output_dir = Path(test_config["archive"]["output_dir"])
            compressed_files = list(output_dir.glob("content/**/*.gz"))
            assert len(compressed_files) > 0
        finally:
            await indexer.close()
            if Path(test_config["archive"]["output_dir"]).exists():
                shutil.rmtree(test_config["archive"]["output_dir"])

    @pytest.mark.asyncio
    async def test_directory_organization(self, test_config, sample_transformed_content):
        """Test that files are organized by date."""
        indexer = ContentIndexer(test_config)
        
        try:
            await indexer.index(sample_transformed_content)
            
            # Check directory structure: YYYY/MM/DD
            output_dir = Path(test_config["archive"]["output_dir"])
            date_dirs = list(output_dir.glob("content/2009/*/*"))
            assert len(date_dirs) > 0
        finally:
            await indexer.close()
            if Path(test_config["archive"]["output_dir"]).exists():
                shutil.rmtree(test_config["archive"]["output_dir"])