"""Tests for transformation module."""

import pytest
from chronos_archiver.transformation import ContentTransformation
from chronos_archiver.models import ArchiveStatus


class TestContentTransformation:
    """Test ContentTransformation class."""

    @pytest.mark.asyncio
    async def test_transform_success(self, test_config, sample_downloaded_content):
        """Test successful content transformation."""
        transformation = ContentTransformation(test_config)
        
        transformed = await transformation.transform(sample_downloaded_content)
        
        assert transformed is not None
        assert transformed.content is not None
        assert transformed.metadata["title"] == "DAR - Diocese Anglicana do Recife"
        assert sample_downloaded_content.snapshot.status == ArchiveStatus.TRANSFORMED

    @pytest.mark.asyncio
    async def test_link_rewriting(self, test_config, sample_downloaded_content):
        """Test that links are properly rewritten."""
        transformation = ContentTransformation(test_config)
        
        transformed = await transformation.transform(sample_downloaded_content)
        
        # Check that relative links are rewritten
        assert "/20090430060114/http://www.dar.org.br/css/style.css" in transformed.content
        assert "/20090430060114/http://www.dar.org.br/sobre" in transformed.content
        assert "/20090430060114/http://www.dar.org.br/images/logo.png" in transformed.content

    @pytest.mark.asyncio
    async def test_metadata_extraction(self, test_config, sample_downloaded_content):
        """Test metadata extraction."""
        transformation = ContentTransformation(test_config)
        
        transformed = await transformation.transform(sample_downloaded_content)
        
        assert "title" in transformed.metadata
        assert transformed.metadata["title"] == "DAR - Diocese Anglicana do Recife"
        assert "description" in transformed.metadata
        assert transformed.metadata["language"] == "pt-BR"

    @pytest.mark.asyncio
    async def test_text_extraction(self, test_config, sample_downloaded_content):
        """Test plain text extraction."""
        transformation = ContentTransformation(test_config)
        
        transformed = await transformation.transform(sample_downloaded_content)
        
        assert transformed.text_content is not None
        assert "Diocese Anglicana do Recife" in transformed.text_content
        assert "Bem-vindo à DAR" in transformed.text_content
        # Scripts should be removed from text
        assert "main.js" not in transformed.text_content

    @pytest.mark.asyncio
    async def test_link_extraction(self, test_config, sample_downloaded_content):
        """Test link extraction."""
        transformation = ContentTransformation(test_config)
        
        transformed = await transformation.transform(sample_downloaded_content)
        
        assert len(transformed.links) > 0
        # Check that various types of links are extracted
        assert any("css" in link for link in transformed.links)
        assert any("sobre" in link for link in transformed.links)

    @pytest.mark.asyncio
    async def test_script_removal(self, test_config, sample_downloaded_content):
        """Test script tag removal."""
        test_config["transformation"]["remove_scripts"] = True
        transformation = ContentTransformation(test_config)
        
        transformed = await transformation.transform(sample_downloaded_content)
        
        assert "<script" not in transformed.content.lower()

    @pytest.mark.asyncio
    async def test_encoding_fallback(self, test_config, sample_snapshot):
        """Test encoding fallback for problematic content."""
        from chronos_archiver.models import DownloadedContent
        
        # Create content with problematic encoding
        problematic_content = "Ação".encode("latin-1")
        downloaded = DownloadedContent(
            snapshot=sample_snapshot,
            content=problematic_content,
            headers={},
            encoding="utf-8",  # Wrong encoding specified
        )
        
        transformation = ContentTransformation(test_config)
        transformed = await transformation.transform(downloaded)
        
        # Should still succeed with fallback encoding
        assert transformed is not None

    @pytest.mark.asyncio
    async def test_absolute_url_rewriting(self, test_config, sample_downloaded_content):
        """Test rewriting of absolute URLs."""
        transformation = ContentTransformation(test_config)
        
        transformed = await transformation.transform(sample_downloaded_content)
        
        # External link should also be rewritten
        assert "/20090430060114/http://www.ieab.org.br/" in transformed.content

    @pytest.mark.asyncio
    async def test_skip_special_urls(self, test_config):
        """Test that special URLs are not rewritten."""
        transformation = ContentTransformation(test_config)
        snapshot = sample_downloaded_content.snapshot
        
        # These should not be rewritten
        assert transformation._rewrite_url("#anchor", snapshot) is None
        assert transformation._rewrite_url("javascript:void(0)", snapshot) is None
        assert transformation._rewrite_url("mailto:test@example.com", snapshot) is None
        assert transformation._rewrite_url("data:image/png;base64,ABC", snapshot) is None