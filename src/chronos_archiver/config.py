"""Configuration management for ChronosArchiver."""

import os
from pathlib import Path
from typing import Any, Optional

import yaml
from pydantic import BaseModel, Field, field_validator


class ArchiveConfig(BaseModel):
    """Archive configuration."""

    output_dir: str = "./archive"
    user_agent: str = "ChronosArchiver/1.0"
    max_file_size: int = 100  # MB
    allowed_mime_types: list[str] = Field(default_factory=list)


class QueueConfig(BaseModel):
    """Queue configuration."""

    backend: str = "redis"
    redis_url: str = "redis://localhost:6379/0"
    redis_db: int = 0
    discovery_queue: str = "chronos:discovery"
    ingestion_queue: str = "chronos:ingestion"
    transformation_queue: str = "chronos:transformation"
    indexing_queue: str = "chronos:indexing"
    max_queue_size: int = 10000
    message_ttl: int = 86400


class ProcessingConfig(BaseModel):
    """Processing configuration."""

    workers: int = 4
    batch_size: int = 10
    retry_attempts: int = 3
    retry_delay: int = 5
    retry_backoff: int = 2
    requests_per_second: int = 5
    concurrent_requests: int = 10
    request_timeout: int = 30
    download_timeout: int = 300


class DatabaseConfig(BaseModel):
    """Database configuration."""

    type: str = "sqlite"
    sqlite_path: str = "./archive/chronos.db"
    pool_size: int = 5
    max_overflow: int = 10


class DiscoveryConfig(BaseModel):
    """Discovery stage configuration."""

    cdx_api_url: str = "https://web.archive.org/cdx/search/cdx"
    cdx_params: dict[str, str] = Field(
        default_factory=lambda: {
            "output": "json",
            "fl": "timestamp,original,mimetype,statuscode,digest,length",
        }
    )
    filter_status_codes: list[int] = Field(default_factory=lambda: [200, 301, 302])
    deduplicate_snapshots: bool = True


class IngestionConfig(BaseModel):
    """Ingestion stage configuration."""

    wayback_url: str = "https://web.archive.org/web"
    verify_ssl: bool = True
    follow_redirects: bool = True
    validate_mime_type: bool = True
    validate_content_hash: bool = True


class TransformationConfig(BaseModel):
    """Transformation stage configuration."""

    rewrite_links: bool = True
    make_links_relative: bool = True
    extract_metadata: bool = True
    extract_text: bool = True
    prettify_html: bool = False
    remove_scripts: bool = False
    remove_comments: bool = True


class IndexingConfig(BaseModel):
    """Indexing stage configuration."""

    enable_full_text_search: bool = True
    index_fields: list[str] = Field(
        default_factory=lambda: ["url", "title", "timestamp", "content", "metadata"]
    )
    compress_content: bool = True
    compression_level: int = 6


class LoggingConfig(BaseModel):
    """Logging configuration."""

    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_to_file: bool = True
    log_file: str = "./logs/chronos.log"
    rotate_logs: bool = True
    max_log_size: int = 10485760
    backup_count: int = 5


class ChronosConfig(BaseModel):
    """Main configuration model."""

    archive: ArchiveConfig = Field(default_factory=ArchiveConfig)
    queue: QueueConfig = Field(default_factory=QueueConfig)
    processing: ProcessingConfig = Field(default_factory=ProcessingConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    discovery: DiscoveryConfig = Field(default_factory=DiscoveryConfig)
    ingestion: IngestionConfig = Field(default_factory=IngestionConfig)
    transformation: TransformationConfig = Field(default_factory=TransformationConfig)
    indexing: IndexingConfig = Field(default_factory=IndexingConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)


def load_config(config_path: Optional[str] = None) -> dict[str, Any]:
    """Load configuration from YAML file.

    Args:
        config_path: Path to configuration file. If None, looks for config.yaml
                    in current directory, then uses defaults.

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If specified config file doesn't exist
        yaml.YAMLError: If config file is invalid YAML
    """
    if config_path:
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
    else:
        # Try default locations
        config_file = Path("config.yaml")
        if not config_file.exists():
            config_file = Path.home() / ".chronos" / "config.yaml"
            if not config_file.exists():
                # Use defaults
                return ChronosConfig().model_dump()

    # Load YAML
    with open(config_file) as f:
        config_data = yaml.safe_load(f)

    # Validate with Pydantic
    config = ChronosConfig(**config_data)
    return config.model_dump()


def save_config(config: dict[str, Any], config_path: str) -> None:
    """Save configuration to YAML file.

    Args:
        config: Configuration dictionary
        config_path: Path to save configuration file
    """
    # Validate first
    validated_config = ChronosConfig(**config)

    # Create directory if needed
    config_file = Path(config_path)
    config_file.parent.mkdir(parents=True, exist_ok=True)

    # Save to YAML
    with open(config_file, "w") as f:
        yaml.dump(validated_config.model_dump(), f, default_flow_style=False, sort_keys=False)


def get_default_config() -> dict[str, Any]:
    """Get default configuration.

    Returns:
        Default configuration dictionary
    """
    return ChronosConfig().model_dump()