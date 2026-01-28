"""Tests for utility functions."""

import pytest
from datetime import datetime
from pathlib import Path
from chronos_archiver.utils import (
    parse_wayback_url,
    build_wayback_url,
    normalize_url,
    extract_domain,
    is_valid_url,
    calculate_hash,
    format_timestamp,
    sanitize_filename,
    format_bytes,
)


class TestUtils:
    """Test utility functions."""

    def test_parse_wayback_url(self):
        """Test parsing Wayback Machine URLs."""
        url = "https://web.archive.org/web/20090430060114/http://www.dar.org.br/"
        parsed = parse_wayback_url(url)
        
        assert parsed is not None
        assert parsed["timestamp"] == "20090430060114"
        assert parsed["original_url"] == "http://www.dar.org.br/"

    def test_parse_wayback_url_with_modifier(self):
        """Test parsing Wayback URLs with modifiers."""
        url = "https://web.archive.org/web/20041022131803fw_/http://www.ieabrecife.com.br/"
        parsed = parse_wayback_url(url)
        
        assert parsed is not None
        assert parsed["timestamp"] == "20041022131803"
        assert parsed["original_url"] == "http://www.ieabrecife.com.br/"

    def test_build_wayback_url(self):
        """Test building Wayback Machine URLs."""
        url = build_wayback_url("20090430060114", "http://www.dar.org.br/")
        
        assert url == "https://web.archive.org/web/20090430060114/http://www.dar.org.br/"

    def test_normalize_url(self):
        """Test URL normalization."""
        assert normalize_url("HTTP://EXAMPLE.COM/") == "http://example.com"
        assert normalize_url("http://example.com:80/") == "http://example.com"
        assert normalize_url("https://example.com:443/") == "https://example.com"

    def test_extract_domain(self):
        """Test domain extraction."""
        assert extract_domain("http://www.dar.org.br/page") == "www.dar.org.br"
        assert extract_domain("https://example.com:8080/") == "example.com:8080"

    def test_is_valid_url(self):
        """Test URL validation."""
        assert is_valid_url("http://example.com") is True
        assert is_valid_url("https://example.com/page") is True
        assert is_valid_url("not-a-url") is False
        assert is_valid_url("//example.com") is False

    def test_calculate_hash(self):
        """Test hash calculation."""
        content = b"Hello, World!"
        hash_sha256 = calculate_hash(content, "sha256")
        hash_md5 = calculate_hash(content, "md5")
        
        assert len(hash_sha256) == 64  # SHA-256 produces 64 hex characters
        assert len(hash_md5) == 32  # MD5 produces 32 hex characters

    def test_format_timestamp(self):
        """Test timestamp formatting."""
        dt = format_timestamp("20090430060114")
        
        assert isinstance(dt, datetime)
        assert dt.year == 2009
        assert dt.month == 4
        assert dt.day == 30
        assert dt.hour == 6
        assert dt.minute == 1
        assert dt.second == 14

    def test_sanitize_filename(self):
        """Test filename sanitization."""
        assert sanitize_filename("file<>name.txt") == "file__name.txt"
        assert sanitize_filename('file"name.txt') == "file_name.txt"
        assert sanitize_filename("file/name.txt") == "file_name.txt"
        
        # Test length limit
        long_name = "a" * 300 + ".txt"
        sanitized = sanitize_filename(long_name)
        assert len(sanitized) <= 255

    def test_format_bytes(self):
        """Test byte formatting."""
        assert format_bytes(100) == "100.0 B"
        assert format_bytes(1024) == "1.0 KB"
        assert format_bytes(1024 * 1024) == "1.0 MB"
        assert format_bytes(1024 * 1024 * 1024) == "1.0 GB"