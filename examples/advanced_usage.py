#!/usr/bin/env python
"""Advanced usage examples for ChronosArchiver."""

import asyncio
from pathlib import Path

from chronos_archiver import ChronosArchiver
from chronos_archiver.config import load_config, save_config
from chronos_archiver.models import ProcessingStats
from chronos_archiver.queue_manager import QueueManager
from chronos_archiver.utils import setup_logging


async def example_1_custom_configuration():
    """Example 1: Use custom configuration."""
    print("\n=== Example 1: Custom Configuration ===")

    # Create custom config
    config = {
        "archive": {
            "output_dir": "./my_archive",
            "user_agent": "MyCustomArchiver/1.0",
            "max_file_size": 50,  # 50 MB
        },
        "processing": {
            "workers": 8,
            "batch_size": 20,
            "requests_per_second": 10,
        },
        "database": {
            "type": "sqlite",
            "sqlite_path": "./my_archive/custom.db",
        },
    }

    # Save configuration
    save_config(config, "my_config.yaml")
    print("✓ Created custom configuration")

    # Load and use it
    loaded_config = load_config("my_config.yaml")
    archiver = ChronosArchiver(loaded_config)

    print(f"  Output dir: {loaded_config['archive']['output_dir']}")
    print(f"  Workers: {loaded_config['processing']['workers']}")


async def example_2_batch_processing():
    """Example 2: Batch process URLs from file."""
    print("\n=== Example 2: Batch Processing ===")

    config = load_config()
    archiver = ChronosArchiver(config)

    # Read URLs from file
    urls_file = Path("examples/sample_sites.txt")
    if urls_file.exists():
        urls = []
        with open(urls_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    urls.append(line)

        print(f"Processing {len(urls)} URLs from file...")

        # Process in batches
        batch_size = 3
        for i in range(0, len(urls), batch_size):
            batch = urls[i:i+batch_size]
            print(f"\nBatch {i//batch_size + 1}:")
            await archiver.archive_urls(batch)
            print(f"  ✓ Completed {len(batch)} URLs")

        await archiver.shutdown()
    else:
        print(f"  Sample sites file not found: {urls_file}")


async def example_3_queue_based_processing():
    """Example 3: Queue-based async processing."""
    print("\n=== Example 3: Queue-based Processing ===")

    config = load_config()
    queue_manager = QueueManager(config)

    # Connect to queue
    await queue_manager.connect()

    # Enqueue some tasks
    urls = [
        "https://web.archive.org/web/20090430060114/http://www.dar.org.br/",
        "https://web.archive.org/web/20120302052501/http://www.dar.org.br/",
    ]

    for url in urls:
        await queue_manager.enqueue(
            "discovery",
            "discover_url",
            {"url": url}
        )

    print(f"✓ Enqueued {len(urls)} tasks")

    # Check queue size
    size = await queue_manager.queue_size("discovery")
    print(f"  Discovery queue size: {size}")

    await queue_manager.disconnect()


async def example_4_error_handling_and_retries():
    """Example 4: Error handling with retries."""
    print("\n=== Example 4: Error Handling ===")

    config = load_config()
    config["processing"]["retry_attempts"] = 5
    config["processing"]["retry_delay"] = 2

    archiver = ChronosArchiver(config)

    # Try to archive a potentially problematic URL
    url = "https://web.archive.org/web/20000101000000/http://invalid-url.example/"

    try:
        await archiver.archive_url(url)
        print("✓ Archive successful")
    except Exception as e:
        print(f"✗ Archive failed: {e}")
        print("  This is expected for invalid URLs")

    await archiver.shutdown()


async def example_5_monitoring_progress():
    """Example 5: Monitor processing progress."""
    print("\n=== Example 5: Progress Monitoring ===")

    config = load_config()
    archiver = ChronosArchiver(config)

    # Initialize stats
    stats = ProcessingStats()

    urls = [
        "https://web.archive.org/web/20090430060114/http://www.dar.org.br/",
        "https://web.archive.org/web/20120302052501/http://www.dar.org.br/",
        "https://web.archive.org/web/20150406103050/http://dar.org.br/",
    ]

    stats.total_snapshots = len(urls)

    for i, url in enumerate(urls, 1):
        print(f"\nProcessing {i}/{len(urls)}: {url}")
        try:
            await archiver.archive_url(url)
            stats.indexed += 1
            print(f"  ✓ Success (Total: {stats.indexed}/{stats.total_snapshots})")
        except Exception as e:
            stats.failed += 1
            print(f"  ✗ Failed: {e}")

    # Calculate success rate
    print(f"\nFinal Stats:")
    print(f"  Total: {stats.total_snapshots}")
    print(f"  Successful: {stats.indexed}")
    print(f"  Failed: {stats.failed}")
    print(f"  Success Rate: {stats.success_rate:.1f}%")

    await archiver.shutdown()


async def example_6_filtering_content():
    """Example 6: Filter content by MIME type."""
    print("\n=== Example 6: Content Filtering ===")

    config = load_config()

    # Only archive HTML and CSS
    config["archive"]["allowed_mime_types"] = [
        "text/html",
        "text/css",
    ]

    archiver = ChronosArchiver(config)

    print("Configured to only archive HTML and CSS files")
    print(f"  Allowed types: {config['archive']['allowed_mime_types']}")

    # This would filter out images, JavaScript, etc.
    url = "https://web.archive.org/web/20090430060114/http://www.dar.org.br/"
    await archiver.archive_url(url)

    await archiver.shutdown()


if __name__ == "__main__":
    print("ChronosArchiver - Advanced Usage Examples")
    print("==========================================")

    # Run examples (uncomment to execute)

    # asyncio.run(example_1_custom_configuration())
    # asyncio.run(example_2_batch_processing())
    # asyncio.run(example_3_queue_based_processing())
    # asyncio.run(example_4_error_handling_and_retries())
    asyncio.run(example_5_monitoring_progress())
    # asyncio.run(example_6_filtering_content())

    print("\n✓ Advanced examples complete!")