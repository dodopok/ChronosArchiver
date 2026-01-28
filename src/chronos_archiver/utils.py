"""Utility functions for ChronosArchiver."""

import hashlib
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse


def setup_logging(config: dict) -> logging.Logger:
    """Set up logging configuration.

    Args:
        config: Logging configuration dictionary

    Returns:
        Configured logger instance
    """
    log_config = config.get("logging", {})
    level = log_config.get("level", "INFO")
    format_str = log_config.get(
        "format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Create logger
    logger = logging.getLogger("chronos_archiver")
    logger.setLevel(getattr(logging, level))

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(format_str))
    logger.addHandler(console_handler)

    # File handler if enabled
    if log_config.get("log_to_file", False):
        log_file = Path(log_config.get("log_file", "./logs/chronos.log"))
        log_file.parent.mkdir(parents=True, exist_ok=True)

        if log_config.get("rotate_logs", False):
            from logging.handlers import RotatingFileHandler

            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=log_config.get("max_log_size", 10485760),
                backupCount=log_config.get("backup_count", 5),
            )
        else:
            file_handler = logging.FileHandler(log_file)

        file_handler.setFormatter(logging.Formatter(format_str))
        logger.addHandler(file_handler)

    return logger


def parse_wayback_url(url: str) -> Optional[dict]:
    """Parse a Wayback Machine URL.

    Args:
        url: Wayback Machine URL

    Returns:
        Dictionary with parsed components or None if invalid

    Example:
        >>> parse_wayback_url('https://web.archive.org/web/20090430060114/http://www.dar.org.br/')
        {'timestamp': '20090430060114', 'original_url': 'http://www.dar.org.br/'}
    """
    pattern = r"https?://web\.archive\.org/web/(\d+)(?:\w+_)?/(.+)"
    match = re.match(pattern, url)

    if match:
        return {"timestamp": match.group(1), "original_url": match.group(2)}
    return None


def build_wayback_url(timestamp: str, original_url: str, modifier: str = "") -> str:
    """Build a Wayback Machine URL.

    Args:
        timestamp: Timestamp in YYYYMMDDhhmmss format
        original_url: Original URL to archive
        modifier: Optional modifier (e.g., 'id_', 'if_')

    Returns:
        Complete Wayback Machine URL
    """
    base = "https://web.archive.org/web"
    return f"{base}/{timestamp}{modifier}/{original_url}"


def normalize_url(url: str) -> str:
    """Normalize a URL for consistent comparison.

    Args:
        url: URL to normalize

    Returns:
        Normalized URL
    """
    # Remove trailing slashes, convert to lowercase
    normalized = url.rstrip("/").lower()

    # Remove default ports
    normalized = re.sub(r":80(/|$)", r"\1", normalized)
    normalized = re.sub(r":443(/|$)", r"\1", normalized)

    return normalized


def extract_domain(url: str) -> str:
    """Extract domain from URL.

    Args:
        url: URL to extract domain from

    Returns:
        Domain name
    """
    parsed = urlparse(url)
    return parsed.netloc


def is_valid_url(url: str) -> bool:
    """Check if URL is valid.

    Args:
        url: URL to validate

    Returns:
        True if valid, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def calculate_hash(content: bytes, algorithm: str = "sha256") -> str:
    """Calculate hash of content.

    Args:
        content: Content to hash
        algorithm: Hash algorithm (sha256, md5, etc.)

    Returns:
        Hexadecimal hash string
    """
    hasher = hashlib.new(algorithm)
    hasher.update(content)
    return hasher.hexdigest()


def format_timestamp(timestamp: str) -> datetime:
    """Convert Wayback timestamp to datetime.

    Args:
        timestamp: Wayback timestamp (YYYYMMDDhhmmss)

    Returns:
        datetime object
    """
    return datetime.strptime(timestamp, "%Y%m%d%H%M%S")


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe filesystem storage.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Remove invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', "_", filename)

    # Limit length
    if len(sanitized) > 255:
        name, ext = sanitized.rsplit(".", 1) if "." in sanitized else (sanitized, "")
        sanitized = name[:250] + ("." + ext if ext else "")

    return sanitized


def ensure_directory(path: Path) -> None:
    """Ensure directory exists, create if necessary.

    Args:
        path: Directory path
    """
    path.mkdir(parents=True, exist_ok=True)


def format_bytes(size: int) -> str:
    """Format byte size in human-readable format.

    Args:
        size: Size in bytes

    Returns:
        Formatted string (e.g., '1.5 MB')
    """
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PB"


def retry_on_exception(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Decorator for retrying functions on exception.

    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Backoff multiplier for delay
    """
    import asyncio
    import functools

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff

            raise last_exception

        return wrapper

    return decorator