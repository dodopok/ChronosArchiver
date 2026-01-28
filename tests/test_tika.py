"""Tests for Apache Tika integration."""

import pytest
from unittest.mock import patch, MagicMock
from chronos_archiver.tika import TikaExtractor


class TestTikaExtractor:
    """Test TikaExtractor class."""

    def test_initialization(self, test_config):
        """Test Tika extractor initialization."""
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            extractor = TikaExtractor(test_config)
            
            assert extractor.enabled is True

    def test_initialization_server_unavailable(self, test_config):
        """Test initialization when Tika server is unavailable."""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = Exception("Connection refused")
            
            extractor = TikaExtractor(test_config)
            
            assert extractor.enabled is False

    def test_extract_text(self, test_config):
        """Test text extraction from content."""
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            extractor = TikaExtractor(test_config)
            extractor.enabled = True
            
            with patch('tika.parser.from_buffer') as mock_parser:
                mock_parser.return_value = {
                    "content": "Extracted text content",
                    "metadata": {
                        "Author": "Douglas Araujo",
                        "title": "Test Document",
                        "Creation-Date": "2024-01-01",
                    }
                }
                
                result = extractor.extract_text(b"test content")
                
                assert result["text"] == "Extracted text content"
                assert result["metadata"]["author"] == "Douglas Araujo"
                assert result["metadata"]["title"] == "Test Document"

    def test_detect_mime_type(self, test_config):
        """Test MIME type detection."""
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            extractor = TikaExtractor(test_config)
            extractor.enabled = True
            
            with patch('tika.detector.from_buffer') as mock_detector:
                mock_detector.return_value = "application/pdf"
                
                mime_type = extractor.detect_mime_type(b"PDF content")
                
                assert mime_type == "application/pdf"

    @pytest.mark.asyncio
    async def test_extract_from_downloaded(self, test_config, sample_downloaded_content):
        """Test extraction from downloaded content."""
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            extractor = TikaExtractor(test_config)
            extractor.enabled = True
            
            with patch('tika.parser.from_buffer') as mock_parser:
                mock_parser.return_value = {
                    "content": "Extracted content",
                    "metadata": {"title": "Test"}
                }
                
                result = await extractor.extract_from_downloaded(sample_downloaded_content)
                
                assert "text" in result
                assert "metadata" in result