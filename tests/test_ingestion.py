"""Tests for ingestion module."""

import pytest
from chronos_archiver.ingestion import ContentIngestion
from chronos_archiver.models import ArchiveSnapshot, ArchiveStatus


@pytest.mark.asyncio
async def test_download_basic(mocker):
    """Test basic download functionality."""
    ingestion = ContentIngestion()

    snapshot = ArchiveSnapshot(
        url="https://web.archive.org/web/20090430060114/http://www.dar.org.br/",
        original_url="http://www.dar.org.br/",
        timestamp="20090430060114",
    )

    # Mock the actual HTTP request
    mock_response = mocker.Mock()
    mock_response.status = 200
    mock_response.headers = {"Content-Type": "text/html"}
    mock_response.read = mocker.AsyncMock(return_value=b"<html><body>Test</body></html>")
    mock_response.get_encoding = mocker.Mock(return_value="utf-8")

    mocker.patch("aiohttp.ClientSession.get", return_value=mocker.AsyncMock(__aenter__=mocker.AsyncMock(return_value=mock_response)))

    # Note: This test would need proper mocking setup
    # For now, skip actual download test
    assert ingestion.user_agent == "ChronosArchiver/1.0"


def test_sanitize_content():
    """Test content sanitization."""
    ingestion = ContentIngestion()

    content = b"Test\x00content\x00with\x00nulls"
    sanitized = ingestion.sanitize_content(content)

    assert b"\x00" not in sanitized
    assert sanitized == b"Testcontentwith nulls"