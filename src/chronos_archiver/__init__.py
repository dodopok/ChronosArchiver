"""ChronosArchiver - An archival system for the Wayback Machine."""

from chronos_archiver.discovery import WaybackDiscovery
from chronos_archiver.indexing import ContentIndexer
from chronos_archiver.ingestion import ContentIngestion
from chronos_archiver.models import ArchiveSnapshot, ArchiveStatus, QueueMessage
from chronos_archiver.queue_manager import QueueManager
from chronos_archiver.transformation import ContentTransformation

__version__ = "1.0.0"
__author__ = "Douglas Araujo"
__email__ = "douglas@example.com"

__all__ = [
    "WaybackDiscovery",
    "ContentIngestion",
    "ContentTransformation",
    "ContentIndexer",
    "QueueManager",
    "ArchiveSnapshot",
    "ArchiveStatus",
    "QueueMessage",
]


class ChronosArchiver:
    """Main archiver class orchestrating the 4-stage pipeline."""

    def __init__(self, config: dict) -> None:
        """Initialize ChronosArchiver with configuration.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.queue_manager = QueueManager(config)
        self.discovery = WaybackDiscovery(config)
        self.ingestion = ContentIngestion(config)
        self.transformation = ContentTransformation(config)
        self.indexer = ContentIndexer(config)

    async def archive_url(self, url: str) -> None:
        """Archive a single URL through the complete pipeline.

        Args:
            url: Wayback Machine URL to archive
        """
        # Stage 1: Discovery
        snapshots = await self.discovery.find_snapshots(url)

        for snapshot in snapshots:
            # Stage 2: Ingestion
            content = await self.ingestion.download(snapshot)

            if content:
                # Stage 3: Transformation
                transformed = await self.transformation.transform(content)

                # Stage 4: Indexing
                await self.indexer.index(transformed)

    async def archive_urls(self, urls: list[str]) -> None:
        """Archive multiple URLs concurrently.

        Args:
            urls: List of Wayback Machine URLs to archive
        """
        import asyncio

        tasks = [self.archive_url(url) for url in urls]
        await asyncio.gather(*tasks)

    async def start_workers(self, worker_count: int = 4) -> None:
        """Start background workers for async processing.

        Args:
            worker_count: Number of workers to start
        """
        await self.queue_manager.start_workers(worker_count)

    async def shutdown(self) -> None:
        """Gracefully shutdown the archiver and all workers."""
        await self.queue_manager.shutdown()
        await self.indexer.close()