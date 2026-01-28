"""ChronosArchiver - Sistema de arquivamento inteligente para a Wayback Machine.

ChronosArchiver - Intelligent archival system for the Wayback Machine.
"""

from chronos_archiver.discovery import WaybackDiscovery
from chronos_archiver.indexing import ContentIndexer
from chronos_archiver.ingestion import ContentIngestion
from chronos_archiver.intelligence import IntelligenceEngine
from chronos_archiver.models import (
    ArchiveSnapshot,
    ArchiveStatus,
    ContentAnalysis,
    MediaEmbed,
    QueueMessage,
    SearchResult,
)
from chronos_archiver.queue_manager import QueueManager
from chronos_archiver.search import SearchEngine
from chronos_archiver.tika import TikaExtractor
from chronos_archiver.transformation import ContentTransformation

__version__ = "1.1.0"
__author__ = "Douglas Araujo"
__email__ = "douglas@example.com"

__all__ = [
    "WaybackDiscovery",
    "ContentIngestion",
    "ContentTransformation",
    "ContentIndexer",
    "IntelligenceEngine",
    "SearchEngine",
    "TikaExtractor",
    "QueueManager",
    "ArchiveSnapshot",
    "ArchiveStatus",
    "ContentAnalysis",
    "MediaEmbed",
    "QueueMessage",
    "SearchResult",
    "ChronosArchiver",
]


class ChronosArchiver:
    """Sistema principal de arquivamento / Main archiver system.
    
    Orquestra o pipeline de 4 estágios com motor de inteligência integrado.
    Orchestrates the 4-stage pipeline with integrated intelligence engine.
    """

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
        
        # Advanced features
        self.intelligence = IntelligenceEngine(config)
        self.search = SearchEngine(config)
        self.tika = TikaExtractor(config)

    async def archive_url(self, url: str, enable_intelligence: bool = True) -> None:
        """Archive a single URL through the complete pipeline.
        
        Arquiva uma URL através do pipeline completo.

        Args:
            url: Wayback Machine URL to archive
            enable_intelligence: Enable intelligence analysis
        """
        # Stage 1: Discovery
        snapshots = await self.discovery.find_snapshots(url)

        for snapshot in snapshots:
            # Stage 2: Ingestion
            content = await self.ingestion.download(snapshot)

            if content:
                # Optional: Tika extraction for non-HTML content
                if self.tika.enabled and snapshot.mime_type != "text/html":
                    tika_result = await self.tika.extract_from_downloaded(content)
                    if tika_result.get("text"):
                        # Enhance content with Tika extraction
                        content.content = tika_result["text"].encode("utf-8")
                
                # Stage 3: Transformation
                transformed = await self.transformation.transform(content)

                if transformed:
                    # Optional: Intelligence analysis
                    if enable_intelligence:
                        analysis = await self.intelligence.analyze(transformed)
                        
                        # Index in search engine
                        await self.search.index_content(analysis)
                    
                    # Stage 4: Indexing
                    await self.indexer.index(transformed)

    async def archive_urls(self, urls: list[str], enable_intelligence: bool = True) -> None:
        """Archive multiple URLs concurrently.
        
        Arquiva múltiplas URLs simultaneamente.

        Args:
            urls: List of Wayback Machine URLs to archive
            enable_intelligence: Enable intelligence analysis
        """
        import asyncio

        tasks = [self.archive_url(url, enable_intelligence) for url in urls]
        await asyncio.gather(*tasks)

    async def search_content(self, query: str, **kwargs) -> list:
        """Search archived content.
        
        Buscar conteúdo arquivado.
        
        Args:
            query: Search query
            **kwargs: Additional search parameters
            
        Returns:
            List of search results
        """
        return await self.search.search(query, **kwargs)

    async def start_workers(self, worker_count: int = 4) -> None:
        """Start background workers for async processing.

        Args:
            worker_count: Number of workers to start
        """
        await self.queue_manager.start_workers(worker_count)

    async def shutdown(self) -> None:
        """Gracefully shutdown the archiver and all workers.
        
        Desligar graciosamente o arquivador e todos os workers.
        """
        await self.queue_manager.shutdown()
        await self.indexer.close()