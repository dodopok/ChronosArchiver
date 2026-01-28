"""Apache Tika integration for advanced text and metadata extraction."""

import logging
from typing import Any, Optional

import requests
from tika import parser as tika_parser
from tika import detector as tika_detector

from chronos_archiver.models import DownloadedContent

logger = logging.getLogger(__name__)


class TikaExtractor:
    """Apache Tika integration for text and metadata extraction.
    
    Provides advanced extraction capabilities:
    - Text extraction from various formats (PDF, DOC, etc.)
    - Metadata extraction (author, creation date, etc.)
    - Language detection
    - MIME type detection
    """

    def __init__(self, config: Optional[dict] = None) -> None:
        """Initialize Tika extractor.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        tika_config = self.config.get("tika", {})
        
        self.enabled = tika_config.get("enabled", True)
        self.tika_server_url = tika_config.get("server_url", "http://localhost:9998")
        
        # Test Tika server connection
        if self.enabled:
            try:
                response = requests.get(f"{self.tika_server_url}/tika", timeout=5)
                if response.status_code == 200:
                    logger.info(f"Connected to Tika server: {self.tika_server_url}")
                else:
                    logger.warning(f"Tika server returned status {response.status_code}")
                    self.enabled = False
            except Exception as e:
                logger.warning(f"Tika server not available: {e}. Text extraction will be limited.")
                self.enabled = False

    def extract_text(self, content: bytes, mime_type: Optional[str] = None) -> dict[str, Any]:
        """Extract text and metadata using Tika.
        
        Args:
            content: Raw content bytes
            mime_type: Optional MIME type hint
            
        Returns:
            Dictionary with extracted text and metadata
        """
        if not self.enabled:
            return {"text": "", "metadata": {}}
        
        try:
            # Parse with Tika
            parsed = tika_parser.from_buffer(content)
            
            text = parsed.get("content", "").strip() if parsed.get("content") else ""
            metadata = parsed.get("metadata", {})
            
            # Extract useful metadata
            extracted_metadata = {
                "author": metadata.get("Author", metadata.get("creator", "")),
                "title": metadata.get("title", metadata.get("dc:title", "")),
                "creation_date": metadata.get("Creation-Date", metadata.get("created", "")),
                "modified_date": metadata.get("Last-Modified", metadata.get("modified", "")),
                "language": metadata.get("language", metadata.get("dc:language", "")),
                "content_type": metadata.get("Content-Type", ""),
                "keywords": metadata.get("Keywords", metadata.get("meta:keyword", "")),
            }
            
            # Clean up empty values
            extracted_metadata = {k: v for k, v in extracted_metadata.items() if v}
            
            logger.info(f"Extracted {len(text)} characters with Tika")
            
            return {
                "text": text,
                "metadata": extracted_metadata,
            }
            
        except Exception as e:
            logger.error(f"Tika extraction failed: {e}")
            return {"text": "", "metadata": {}}

    def detect_mime_type(self, content: bytes) -> Optional[str]:
        """Detect MIME type using Tika.
        
        Args:
            content: Raw content bytes
            
        Returns:
            Detected MIME type
        """
        if not self.enabled:
            return None
        
        try:
            mime_type = tika_detector.from_buffer(content)
            logger.info(f"Detected MIME type: {mime_type}")
            return mime_type
        except Exception as e:
            logger.error(f"MIME type detection failed: {e}")
            return None

    async def extract_from_downloaded(self, downloaded: DownloadedContent) -> dict[str, Any]:
        """Extract text and metadata from downloaded content.
        
        Args:
            downloaded: Downloaded content
            
        Returns:
            Extraction results
        """
        return self.extract_text(
            downloaded.content,
            mime_type=downloaded.snapshot.mime_type,
        )