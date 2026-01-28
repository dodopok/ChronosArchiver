"""Tests for transformation module."""

import pytest
from chronos_archiver.models import ArchiveSnapshot, DownloadedContent
from chronos_archiver.transformation import ContentTransformation


@pytest.mark.asyncio
async def test_transform_html():
    """Test HTML transformation."""
    transformation = ContentTransformation()

    snapshot = ArchiveSnapshot(
        url="https://web.archive.org/web/20090430060114/http://www.dar.org.br/",
        original_url="http://www.dar.org.br/",
        timestamp="20090430060114",
    )

    html_content = b"""<!DOCTYPE html>
    <html>
    <head><title>Test Page</title></head>
    <body>
        <a href="/page.html">Link</a>
        <img src="image.jpg" />
    </body>
    </html>"""

    downloaded = DownloadedContent(
        snapshot=snapshot,
        content=html_content,
        headers={},
        encoding="utf-8",
    )

    transformed = await transformation.transform(downloaded)

    assert transformed is not None
    assert transformed.metadata.get("title") == "Test Page"
    assert "<html>" in transformed.content


def test_extract_metadata():
    """Test metadata extraction."""
    from bs4 import BeautifulSoup

    transformation = ContentTransformation()

    html = """
    <html lang="en">
    <head>
        <title>Test Title</title>
        <meta name="description" content="Test description" />
        <meta property="og:title" content="OG Title" />
    </head>
    </html>
    """

    soup = BeautifulSoup(html, "lxml")
    metadata = transformation._extract_metadata(soup)

    assert metadata["title"] == "Test Title"
    assert metadata["description"] == "Test description"
    assert metadata["og:title"] == "OG Title"
    assert metadata["language"] == "en"


def test_extract_text():
    """Test text extraction."""
    from bs4 import BeautifulSoup

    transformation = ContentTransformation()

    html = """
    <html>
    <body>
        <p>This is a test.</p>
        <script>alert('test');</script>
        <p>More content.</p>
    </body>
    </html>
    """

    soup = BeautifulSoup(html, "lxml")
    text = transformation._extract_text(soup)

    assert "This is a test" in text
    assert "More content" in text
    assert "alert" not in text  # Script removed