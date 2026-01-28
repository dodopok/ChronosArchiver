"""Data models for ChronosArchiver."""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, HttpUrl


class ArchiveStatus(str, Enum):
    """Status of archive processing."""

    PENDING = "pending"
    DISCOVERED = "discovered"
    DOWNLOADING = "downloading"
    DOWNLOADED = "downloaded"
    TRANSFORMING = "transforming"
    TRANSFORMED = "transformed"
    INDEXING = "indexing"
    INDEXED = "indexed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ArchiveSnapshot(BaseModel):
    """Represents a snapshot from the Wayback Machine."""

    url: str = Field(..., description="Wayback Machine URL")
    original_url: str = Field(..., description="Original URL")
    timestamp: str = Field(..., description="Snapshot timestamp (YYYYMMDDhhmmss)")
    mime_type: Optional[str] = Field(None, description="MIME type of content")
    status_code: Optional[int] = Field(None, description="HTTP status code")
    digest: Optional[str] = Field(None, description="Content digest/hash")
    length: Optional[int] = Field(None, description="Content length in bytes")
    status: ArchiveStatus = Field(default=ArchiveStatus.DISCOVERED, description="Processing status")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True


class DownloadedContent(BaseModel):
    """Represents downloaded content from Wayback Machine."""

    snapshot: ArchiveSnapshot
    content: bytes = Field(..., description="Raw downloaded content")
    headers: dict[str, str] = Field(default_factory=dict, description="HTTP headers")
    encoding: Optional[str] = Field(None, description="Content encoding")
    downloaded_at: datetime = Field(default_factory=datetime.utcnow)


class TransformedContent(BaseModel):
    """Represents transformed content ready for indexing."""

    snapshot: ArchiveSnapshot
    content: str = Field(..., description="Transformed HTML content")
    text_content: Optional[str] = Field(None, description="Extracted text content")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Extracted metadata")
    links: list[str] = Field(default_factory=list, description="Extracted and rewritten links")
    transformed_at: datetime = Field(default_factory=datetime.utcnow)


class IndexedContent(BaseModel):
    """Represents indexed content in the archive."""

    id: Optional[int] = Field(None, description="Database ID")
    snapshot: ArchiveSnapshot
    content: str = Field(..., description="Stored content")
    text_content: Optional[str] = Field(None, description="Searchable text")
    metadata: dict[str, Any] = Field(default_factory=dict)
    indexed_at: datetime = Field(default_factory=datetime.utcnow)


class QueueMessage(BaseModel):
    """Message for queue-based processing."""

    id: str = Field(..., description="Unique message ID")
    type: str = Field(..., description="Message type")
    payload: dict[str, Any] = Field(..., description="Message payload")
    retry_count: int = Field(default=0, description="Number of retry attempts")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(None, description="Message expiration time")


class ProcessingStats(BaseModel):
    """Statistics for processing pipeline."""

    total_snapshots: int = 0
    discovered: int = 0
    downloaded: int = 0
    transformed: int = 0
    indexed: int = 0
    failed: int = 0
    skipped: int = 0
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None

    @property
    def duration(self) -> Optional[float]:
        """Processing duration in seconds."""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None

    @property
    def success_rate(self) -> float:
        """Success rate as percentage."""
        if self.total_snapshots == 0:
            return 0.0
        return (self.indexed / self.total_snapshots) * 100