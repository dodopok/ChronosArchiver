"""Discovery module - Stage 1: Find URLs using CDX API."""

import asyncio
import logging
from typing import Any, Optional
from urllib.parse import quote, urlparse

import aiohttp

from chronos_archiver.models import ArchiveSnapshot, ArchiveStatus
from chronos_archiver.utils import normalize_url, parse_wayback_url

logger = logging.getLogger(__name__)


class WaybackDiscovery:
    """Discover archived URLs using the Wayback Machine CDX API."""

    def __init__(self, config: Optional[dict] = None) -> None:
        """Initialize discovery module.

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        discovery_config = self.config.get("discovery", {})

        self.cdx_api_url = discovery_config.get(
            "cdx_api_url", "https://web.archive.org/cdx/search/cdx"
        )
        self.cdx_params = discovery_config.get(
            "cdx_params",
            {
                "output": "json",
                "fl": "timestamp,original,mimetype,statuscode,digest,length",
            },
        )
        self.filter_status_codes = discovery_config.get("filter_status_codes", [200, 301, 302])
        self.deduplicate = discovery_config.get("deduplicate_snapshots", True)

        processing_config = self.config.get("processing", {})
        self.timeout = aiohttp.ClientTimeout(total=processing_config.get("request_timeout", 30))

    async def find_snapshots(self, url: str) -> list[ArchiveSnapshot]:
        """Find all snapshots for a given URL or URL pattern.

        Args:
            url: URL or Wayback Machine URL to find snapshots for

        Returns:
            List of discovered snapshots

        Example:
            >>> discovery = WaybackDiscovery()
            >>> snapshots = await discovery.find_snapshots('http://www.dar.org.br/')
        """
        # Parse if it's a Wayback URL
        parsed = parse_wayback_url(url)
        if parsed:
            # Single snapshot
            return [await self._create_snapshot_from_wayback_url(url)]
        else:
            # Query CDX API for all snapshots
            return await self._query_cdx_api(url)

    async def _query_cdx_api(self, url: str) -> list[ArchiveSnapshot]:
        """Query CDX API for snapshots.

        Args:
            url: Original URL to search for

        Returns:
            List of snapshots found
        """
        logger.info(f"Querying CDX API for: {url}")

        # Prepare query parameters
        params = self.cdx_params.copy()
        params["url"] = url

        # Add wildcard for subdirectories if needed
        if url.endswith("/"):
            params["matchType"] = "prefix"

        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            try:
                async with session.get(self.cdx_api_url, params=params) as response:
                    response.raise_for_status()
                    data = await response.json()

                    # Parse CDX response
                    snapshots = self._parse_cdx_response(data)

                    logger.info(f"Found {len(snapshots)} snapshots for {url}")
                    return snapshots

            except aiohttp.ClientError as e:
                logger.error(f"CDX API request failed for {url}: {e}")
                return []
            except Exception as e:
                logger.error(f"Unexpected error querying CDX API: {e}")
                return []

    def _parse_cdx_response(self, data: list[Any]) -> list[ArchiveSnapshot]:
        """Parse CDX JSON response into ArchiveSnapshot objects.

        Args:
            data: CDX API JSON response

        Returns:
            List of parsed snapshots
        """
        snapshots = []
        seen_digests = set()

        # Skip header row if present
        rows = data[1:] if data and isinstance(data[0], list) and data[0][0] == "timestamp" else data

        for row in rows:
            try:
                if len(row) < 6:
                    continue

                timestamp, original, mimetype, statuscode, digest, length = row[:6]

                # Filter by status code
                try:
                    status_int = int(statuscode)
                    if self.filter_status_codes and status_int not in self.filter_status_codes:
                        continue
                except ValueError:
                    continue

                # Deduplicate by digest
                if self.deduplicate and digest in seen_digests:
                    continue

                seen_digests.add(digest)

                # Build Wayback URL
                wayback_url = f"https://web.archive.org/web/{timestamp}/{original}"

                snapshot = ArchiveSnapshot(
                    url=wayback_url,
                    original_url=original,
                    timestamp=timestamp,
                    mime_type=mimetype,
                    status_code=status_int,
                    digest=digest,
                    length=int(length) if length and length.isdigit() else None,
                    status=ArchiveStatus.DISCOVERED,
                )

                snapshots.append(snapshot)

            except Exception as e:
                logger.warning(f"Failed to parse CDX row {row}: {e}")
                continue

        return snapshots

    async def _create_snapshot_from_wayback_url(self, wayback_url: str) -> ArchiveSnapshot:
        """Create a snapshot object from a Wayback Machine URL.

        Args:
            wayback_url: Wayback Machine URL

        Returns:
            ArchiveSnapshot object
        """
        parsed = parse_wayback_url(wayback_url)
        if not parsed:
            raise ValueError(f"Invalid Wayback Machine URL: {wayback_url}")

        return ArchiveSnapshot(
            url=wayback_url,
            original_url=parsed["original_url"],
            timestamp=parsed["timestamp"],
            status=ArchiveStatus.DISCOVERED,
        )

    async def discover_site(self, base_url: str, max_depth: int = 3) -> list[ArchiveSnapshot]:
        """Discover all pages from a site by crawling links.

        Args:
            base_url: Base URL to start discovery from
            max_depth: Maximum crawl depth

        Returns:
            List of all discovered snapshots
        """
        logger.info(f"Starting site discovery for: {base_url}")

        all_snapshots = []
        visited_urls = set()
        queue = [(base_url, 0)]

        while queue:
            url, depth = queue.pop(0)

            if depth > max_depth or normalize_url(url) in visited_urls:
                continue

            visited_urls.add(normalize_url(url))

            # Find snapshots for this URL
            snapshots = await self.find_snapshots(url)
            all_snapshots.extend(snapshots)

            # TODO: Extract links from snapshots and add to queue
            # This would require downloading and parsing content

        logger.info(f"Site discovery complete: {len(all_snapshots)} snapshots found")
        return all_snapshots

    async def batch_discover(self, urls: list[str]) -> list[ArchiveSnapshot]:
        """Discover snapshots for multiple URLs concurrently.

        Args:
            urls: List of URLs to discover

        Returns:
            Combined list of all discovered snapshots
        """
        tasks = [self.find_snapshots(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_snapshots = []
        for result in results:
            if isinstance(result, list):
                all_snapshots.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"Discovery failed: {result}")

        return all_snapshots