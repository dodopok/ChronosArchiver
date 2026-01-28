"""Indexing module - Stage 4: Store and index content."""

import gzip
import json
import logging
from pathlib import Path
from typing import Optional

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    Text,
    create_engine,
    event,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from chronos_archiver.models import ArchiveStatus, IndexedContent, TransformedContent
from chronos_archiver.utils import ensure_directory, format_timestamp, sanitize_filename

logger = logging.getLogger(__name__)

Base = declarative_base()


class ArchivedPage(Base):
    """Database model for archived pages."""

    __tablename__ = "archived_pages"

    id = Column(Integer, primary_key=True)
    url = Column(String(2048), nullable=False, index=True)
    original_url = Column(String(2048), nullable=False, index=True)
    timestamp = Column(String(14), nullable=False, index=True)
    mime_type = Column(String(100))
    status_code = Column(Integer)
    digest = Column(String(64), index=True)
    title = Column(String(500))
    text_content = Column(Text)
    metadata_json = Column(Text)
    file_path = Column(String(1024))
    indexed_at = Column(DateTime, nullable=False)


class ContentIndexer:
    """Index and store archived content."""

    def __init__(self, config: Optional[dict] = None) -> None:
        """Initialize indexing module.

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        db_config = self.config.get("database", {})
        archive_config = self.config.get("archive", {})
        indexing_config = self.config.get("indexing", {})

        self.output_dir = Path(archive_config.get("output_dir", "./archive"))
        self.compress = indexing_config.get("compress_content", True)
        self.compression_level = indexing_config.get("compression_level", 6)

        # Set up database
        db_type = db_config.get("type", "sqlite")
        if db_type == "sqlite":
            db_path = Path(db_config.get("sqlite_path", "./archive/chronos.db"))
            db_path.parent.mkdir(parents=True, exist_ok=True)
            db_url = f"sqlite:///{db_path}"
        else:
            # PostgreSQL or other
            db_url = db_config.get("postgresql_url", "sqlite:///chronos.db")

        self.engine = create_engine(db_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

        # Create output directories
        ensure_directory(self.output_dir)
        ensure_directory(self.output_dir / "content")

    async def index(self, transformed: TransformedContent) -> Optional[IndexedContent]:
        """Index transformed content.

        Args:
            transformed: Transformed content to index

        Returns:
            Indexed content or None if failed

        Example:
            >>> indexer = ContentIndexer()
            >>> indexed = await indexer.index(transformed)
        """
        transformed.snapshot.status = ArchiveStatus.INDEXING
        logger.info(f"Indexing: {transformed.snapshot.url}")

        try:
            # Store content to file
            file_path = await self._store_content(transformed)

            # Save to database
            indexed_id = self._save_to_database(transformed, file_path)

            transformed.snapshot.status = ArchiveStatus.INDEXED
            logger.info(f"Indexed successfully: {transformed.snapshot.url}")

            return IndexedContent(
                id=indexed_id,
                snapshot=transformed.snapshot,
                content=transformed.content,
                text_content=transformed.text_content,
                metadata=transformed.metadata,
            )

        except Exception as e:
            transformed.snapshot.status = ArchiveStatus.FAILED
            logger.error(f"Indexing failed for {transformed.snapshot.url}: {e}")
            return None

    async def _store_content(self, transformed: TransformedContent) -> str:
        """Store content to filesystem.

        Args:
            transformed: Transformed content

        Returns:
            Relative file path
        """
        # Create directory structure: content/YYYY/MM/DD/
        timestamp_dt = format_timestamp(transformed.snapshot.timestamp)
        date_dir = self.output_dir / "content" / timestamp_dt.strftime("%Y/%m/%d")
        ensure_directory(date_dir)

        # Generate filename from URL and timestamp
        filename = sanitize_filename(
            f"{transformed.snapshot.timestamp}_{transformed.snapshot.original_url.split('://')[-1].replace('/', '_')}.html"
        )

        if self.compress:
            filename += ".gz"

        file_path = date_dir / filename

        # Write content
        content_bytes = transformed.content.encode("utf-8")
        if self.compress:
            with gzip.open(file_path, "wb", compresslevel=self.compression_level) as f:
                f.write(content_bytes)
        else:
            with open(file_path, "wb") as f:
                f.write(content_bytes)

        # Return relative path
        return str(file_path.relative_to(self.output_dir))

    def _save_to_database(self, transformed: TransformedContent, file_path: str) -> int:
        """Save metadata to database.

        Args:
            transformed: Transformed content
            file_path: Path to stored file

        Returns:
            Database ID
        """
        session = self.Session()
        try:
            page = ArchivedPage(
                url=transformed.snapshot.url,
                original_url=transformed.snapshot.original_url,
                timestamp=transformed.snapshot.timestamp,
                mime_type=transformed.snapshot.mime_type,
                status_code=transformed.snapshot.status_code,
                digest=transformed.snapshot.digest,
                title=transformed.metadata.get("title"),
                text_content=transformed.text_content,
                metadata_json=json.dumps(transformed.metadata),
                file_path=file_path,
                indexed_at=transformed.transformed_at,
            )

            session.add(page)
            session.commit()
            page_id = page.id
            return page_id

        finally:
            session.close()

    async def search(self, query: str, limit: int = 100) -> list[IndexedContent]:
        """Search indexed content.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of matching indexed content
        """
        session = self.Session()
        try:
            results = (
                session.query(ArchivedPage)
                .filter(
                    (ArchivedPage.text_content.contains(query))
                    | (ArchivedPage.title.contains(query))
                    | (ArchivedPage.original_url.contains(query))
                )
                .limit(limit)
                .all()
            )

            return [
                IndexedContent(
                    id=r.id,
                    snapshot=None,  # Reconstruct if needed
                    content="",
                    text_content=r.text_content,
                    metadata=json.loads(r.metadata_json) if r.metadata_json else {},
                )
                for r in results
            ]

        finally:
            session.close()

    async def close(self) -> None:
        """Close database connections."""
        self.engine.dispose()