"""Transformation module - Stage 3: Transform and enrich content."""

import logging
import re
from typing import Optional
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from chronos_archiver.models import ArchiveStatus, DownloadedContent, TransformedContent
from chronos_archiver.utils import build_wayback_url, parse_wayback_url

logger = logging.getLogger(__name__)


class ContentTransformation:
    """Transform content for local archiving."""

    def __init__(self, config: Optional[dict] = None) -> None:
        """Initialize transformation module.

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        transform_config = self.config.get("transformation", {})

        self.rewrite_links = transform_config.get("rewrite_links", True)
        self.make_relative = transform_config.get("make_links_relative", True)
        self.extract_metadata = transform_config.get("extract_metadata", True)
        self.extract_text = transform_config.get("extract_text", True)
        self.remove_scripts = transform_config.get("remove_scripts", False)
        self.remove_comments = transform_config.get("remove_comments", True)

    async def transform(self, downloaded: DownloadedContent) -> Optional[TransformedContent]:
        """Transform downloaded content.

        Args:
            downloaded: Downloaded content

        Returns:
            Transformed content or None if failed

        Example:
            >>> transformation = ContentTransformation()
            >>> transformed = await transformation.transform(downloaded)
        """
        downloaded.snapshot.status = ArchiveStatus.TRANSFORMING
        logger.info(f"Transforming: {downloaded.snapshot.url}")

        try:
            # Decode content
            encoding = downloaded.encoding or "utf-8"
            try:
                html = downloaded.content.decode(encoding)
            except UnicodeDecodeError:
                # Fallback encodings
                for fallback in ["utf-8", "latin-1", "cp1252"]:
                    try:
                        html = downloaded.content.decode(fallback)
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    logger.error(f"Failed to decode content: {downloaded.snapshot.url}")
                    return None

            # Parse HTML
            soup = BeautifulSoup(html, "lxml")

            # Transform content
            if self.rewrite_links:
                soup = self._rewrite_links(soup, downloaded.snapshot)

            if self.remove_scripts:
                self._remove_scripts(soup)

            if self.remove_comments:
                self._remove_comments(soup)

            # Extract metadata
            metadata = {}
            if self.extract_metadata:
                metadata = self._extract_metadata(soup)

            # Extract text
            text_content = None
            if self.extract_text:
                text_content = self._extract_text(soup)

            # Extract links
            links = self._extract_links(soup)

            # Create transformed content
            transformed = TransformedContent(
                snapshot=downloaded.snapshot,
                content=str(soup),
                text_content=text_content,
                metadata=metadata,
                links=links,
            )

            downloaded.snapshot.status = ArchiveStatus.TRANSFORMED
            logger.info(f"Transformed successfully: {downloaded.snapshot.url}")

            return transformed

        except Exception as e:
            downloaded.snapshot.status = ArchiveStatus.FAILED
            logger.error(f"Transformation failed for {downloaded.snapshot.url}: {e}")
            return None

    def _rewrite_links(self, soup: BeautifulSoup, snapshot) -> BeautifulSoup:
        """Rewrite links to point to archived versions.

        Args:
            soup: BeautifulSoup object
            snapshot: Current snapshot

        Returns:
            Modified BeautifulSoup object
        """
        # Rewrite href attributes
        for tag in soup.find_all(href=True):
            original_href = tag["href"]
            rewritten = self._rewrite_url(original_href, snapshot)
            if rewritten:
                tag["href"] = rewritten

        # Rewrite src attributes
        for tag in soup.find_all(src=True):
            original_src = tag["src"]
            rewritten = self._rewrite_url(original_src, snapshot)
            if rewritten:
                tag["src"] = rewritten

        # Rewrite CSS url() references
        for style_tag in soup.find_all("style"):
            if style_tag.string:
                style_tag.string = self._rewrite_css_urls(style_tag.string, snapshot)

        return soup

    def _rewrite_url(self, url: str, snapshot) -> Optional[str]:
        """Rewrite a single URL.

        Args:
            url: URL to rewrite
            snapshot: Current snapshot

        Returns:
            Rewritten URL or None
        """
        # Skip data URLs, anchors, and javascript
        if url.startswith(("#", "data:", "javascript:", "mailto:")):
            return None

        # Skip already rewritten Wayback URLs
        if "web.archive.org" in url:
            return url

        # Convert relative to absolute
        if not url.startswith(("http://", "https://")):
            base_url = snapshot.original_url
            url = urljoin(base_url, url)

        # Build Wayback URL with same timestamp
        if self.make_relative:
            # Make relative to archive root
            return f"/{snapshot.timestamp}/{url}"
        else:
            return build_wayback_url(snapshot.timestamp, url)

    def _rewrite_css_urls(self, css: str, snapshot) -> str:
        """Rewrite URLs in CSS.

        Args:
            css: CSS content
            snapshot: Current snapshot

        Returns:
            CSS with rewritten URLs
        """
        pattern = r'url\([\'"]?([^\'")]+)[\'"]?\)'

        def replace_url(match):
            url = match.group(1)
            rewritten = self._rewrite_url(url, snapshot)
            return f'url("{rewritten}")' if rewritten else match.group(0)

        return re.sub(pattern, replace_url, css)

    def _extract_metadata(self, soup: BeautifulSoup) -> dict:
        """Extract metadata from HTML.

        Args:
            soup: BeautifulSoup object

        Returns:
            Dictionary of metadata
        """
        metadata = {}

        # Title
        title_tag = soup.find("title")
        if title_tag:
            metadata["title"] = title_tag.get_text(strip=True)

        # Meta tags
        for meta in soup.find_all("meta"):
            name = meta.get("name") or meta.get("property")
            content = meta.get("content")
            if name and content:
                metadata[name] = content

        # Language
        html_tag = soup.find("html")
        if html_tag and html_tag.get("lang"):
            metadata["language"] = html_tag["lang"]

        return metadata

    def _extract_text(self, soup: BeautifulSoup) -> str:
        """Extract plain text from HTML.

        Args:
            soup: BeautifulSoup object

        Returns:
            Plain text content
        """
        # Remove script and style elements
        for element in soup(["script", "style", "meta", "noscript"]):
            element.decompose()

        # Get text
        text = soup.get_text(separator=" ", strip=True)

        # Clean up whitespace
        text = re.sub(r"\s+", " ", text)

        return text

    def _extract_links(self, soup: BeautifulSoup) -> list[str]:
        """Extract all links from HTML.

        Args:
            soup: BeautifulSoup object

        Returns:
            List of URLs
        """
        links = set()

        for tag in soup.find_all(href=True):
            links.add(tag["href"])

        for tag in soup.find_all(src=True):
            links.add(tag["src"])

        return list(links)

    def _remove_scripts(self, soup: BeautifulSoup) -> None:
        """Remove script tags from HTML.

        Args:
            soup: BeautifulSoup object
        """
        for script in soup.find_all("script"):
            script.decompose()

    def _remove_comments(self, soup: BeautifulSoup) -> None:
        """Remove HTML comments.

        Args:
            soup: BeautifulSoup object
        """
        from bs4 import Comment

        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()