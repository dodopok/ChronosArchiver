"""Ingestion module - Stage 2: Download content from Wayback Machine."""

import asyncio
import logging
from typing import Optional

import aiohttp
from asyncio_throttle import Throttler

from chronos_archiver.models import ArchiveSnapshot, ArchiveStatus, DownloadedContent
from chronos_archiver.utils import calculate_hash, retry_on_exception

logger = logging.getLogger(__name__)


class ContentIngestion:
    """Download and validate content from the Wayback Machine."""

    def __init__(self, config: Optional[dict] = None) -> None:
        """Initialize ingestion module.

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        ingestion_config = self.config.get("ingestion", {})
        archive_config = self.config.get("archive", {})
        processing_config = self.config.get("processing", {})

        self.wayback_url = ingestion_config.get("wayback_url", "https://web.archive.org/web")
        self.verify_ssl = ingestion_config.get("verify_ssl", True)
        self.validate_hash = ingestion_config.get("validate_content_hash", True)

        self.user_agent = archive_config.get("user_agent", "ChronosArchiver/1.0")
        self.max_file_size = archive_config.get("max_file_size", 100) * 1024 * 1024  # MB to bytes

        self.timeout = aiohttp.ClientTimeout(
            total=processing_config.get("download_timeout", 300)
        )
        self.max_retries = processing_config.get("retry_attempts", 3)
        self.retry_delay = processing_config.get("retry_delay", 5)

        # Rate limiting
        self.throttler = Throttler(
            rate_limit=processing_config.get("requests_per_second", 5)
        )

    async def download(self, snapshot: ArchiveSnapshot) -> Optional[DownloadedContent]:
        """Download content for a snapshot.

        Args:
            snapshot: Snapshot to download

        Returns:
            Downloaded content or None if failed

        Example:
            >>> ingestion = ContentIngestion()
            >>> content = await ingestion.download(snapshot)
        """
        snapshot.status = ArchiveStatus.DOWNLOADING
        logger.info(f"Downloading: {snapshot.url}")

        try:
            content = await self._download_with_retry(snapshot)
            if content:
                snapshot.status = ArchiveStatus.DOWNLOADED
                logger.info(f"Downloaded successfully: {snapshot.url}")
            return content
        except Exception as e:
            snapshot.status = ArchiveStatus.FAILED
            logger.error(f"Download failed for {snapshot.url}: {e}")
            return None

    @retry_on_exception(max_attempts=3, delay=5.0, backoff=2.0)
    async def _download_with_retry(self, snapshot: ArchiveSnapshot) -> Optional[DownloadedContent]:
        """Download with retry logic.

        Args:
            snapshot: Snapshot to download

        Returns:
            Downloaded content
        """
        async with self.throttler:
            return await self._perform_download(snapshot)

    async def _perform_download(self, snapshot: ArchiveSnapshot) -> Optional[DownloadedContent]:
        """Perform the actual download.

        Args:
            snapshot: Snapshot to download

        Returns:
            Downloaded content
        """
        headers = {"User-Agent": self.user_agent}

        connector = aiohttp.TCPConnector(ssl=self.verify_ssl)
        async with aiohttp.ClientSession(
            connector=connector, timeout=self.timeout, headers=headers
        ) as session:
            async with session.get(snapshot.url) as response:
                response.raise_for_status()

                # Check content length
                content_length = response.headers.get("Content-Length")
                if content_length and int(content_length) > self.max_file_size:
                    logger.warning(
                        f"File too large ({content_length} bytes), skipping: {snapshot.url}"
                    )
                    snapshot.status = ArchiveStatus.SKIPPED
                    return None

                # Download content
                content = await response.read()

                # Validate size
                if len(content) > self.max_file_size:
                    logger.warning(
                        f"Downloaded content too large ({len(content)} bytes), skipping"
                    )
                    snapshot.status = ArchiveStatus.SKIPPED
                    return None

                # Validate hash if digest is available
                if self.validate_hash and snapshot.digest:
                    content_hash = calculate_hash(content, "sha1")
                    if content_hash != snapshot.digest:
                        logger.warning(
                            f"Content hash mismatch for {snapshot.url}: "
                            f"expected {snapshot.digest}, got {content_hash}"
                        )

                # Create downloaded content object
                return DownloadedContent(
                    snapshot=snapshot,
                    content=content,
                    headers=dict(response.headers),
                    encoding=response.get_encoding(),
                )

    async def batch_download(
        self, snapshots: list[ArchiveSnapshot], concurrency: int = 10
    ) -> list[Optional[DownloadedContent]]:
        """Download multiple snapshots concurrently.

        Args:
            snapshots: List of snapshots to download
            concurrency: Maximum concurrent downloads

        Returns:
            List of downloaded content (None for failures)
        """
        semaphore = asyncio.Semaphore(concurrency)

        async def download_with_semaphore(snapshot: ArchiveSnapshot):
            async with semaphore:
                return await self.download(snapshot)

        tasks = [download_with_semaphore(snapshot) for snapshot in snapshots]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions
        downloaded = []
        for result in results:
            if isinstance(result, DownloadedContent):
                downloaded.append(result)
            elif isinstance(result, Exception):
                logger.error(f"Download failed: {result}")
                downloaded.append(None)
            else:
                downloaded.append(result)

        return downloaded

    def sanitize_content(self, content: bytes) -> bytes:
        """Sanitize downloaded content.

        Args:
            content: Raw content bytes

        Returns:
            Sanitized content
        """
        # Remove null bytes
        sanitized = content.replace(b"\x00", b"")

        # TODO: Add more sanitization as needed
        # - Remove malicious scripts
        # - Fix encoding issues
        # - Normalize line endings

        return sanitized