#!/usr/bin/env python
"""Basic usage examples for ChronosArchiver."""

import asyncio

from chronos_archiver import ChronosArchiver
from chronos_archiver.config import load_config
from chronos_archiver.discovery import WaybackDiscovery
from chronos_archiver.indexing import ContentIndexer
from chronos_archiver.ingestion import ContentIngestion
from chronos_archiver.transformation import ContentTransformation


async def example_1_archive_single_url():
    """Example 1: Archive a single URL."""
    print("\n=== Example 1: Archive Single URL ===")

    # Load configuration
    config = load_config()

    # Initialize archiver
    archiver = ChronosArchiver(config)

    # Archive a URL
    url = "https://web.archive.org/web/20090430060114/http://www.dar.org.br/"
    await archiver.archive_url(url)

    print(f"✓ Archived: {url}")

    await archiver.shutdown()


async def example_2_archive_multiple_urls():
    """Example 2: Archive multiple URLs."""
    print("\n=== Example 2: Archive Multiple URLs ===")

    config = load_config()
    archiver = ChronosArchiver(config)

    urls = [
        "https://web.archive.org/web/20090430060114/http://www.dar.org.br/",
        "https://web.archive.org/web/20120302052501/http://www.dar.org.br/",
        "https://web.archive.org/web/20150406103050/http://dar.org.br/",
    ]

    await archiver.archive_urls(urls)

    print(f"✓ Archived {len(urls)} URLs")

    await archiver.shutdown()


async def example_3_manual_pipeline():
    """Example 3: Manually run each stage of the pipeline."""
    print("\n=== Example 3: Manual Pipeline Execution ===")

    config = load_config()

    # Initialize each stage
    discovery = WaybackDiscovery(config)
    ingestion = ContentIngestion(config)
    transformation = ContentTransformation(config)
    indexer = ContentIndexer(config)

    # Stage 1: Discovery
    print("Stage 1: Discovery...")
    url = "https://web.archive.org/web/20090430060114/http://www.dar.org.br/"
    snapshots = await discovery.find_snapshots(url)
    print(f"  Found {len(snapshots)} snapshots")

    for snapshot in snapshots[:1]:  # Process first snapshot only
        # Stage 2: Ingestion
        print("\nStage 2: Ingestion...")
        downloaded = await ingestion.download(snapshot)
        if not downloaded:
            print("  Download failed")
            continue
        print(f"  Downloaded {len(downloaded.content)} bytes")

        # Stage 3: Transformation
        print("\nStage 3: Transformation...")
        transformed = await transformation.transform(downloaded)
        if not transformed:
            print("  Transformation failed")
            continue
        print(f"  Extracted metadata: {transformed.metadata.get('title', 'No title')}")

        # Stage 4: Indexing
        print("\nStage 4: Indexing...")
        indexed = await indexer.index(transformed)
        if indexed:
            print(f"  Indexed with ID: {indexed.id}")

    await indexer.close()
    print("\n✓ Pipeline complete")


async def example_4_search_archived_content():
    """Example 4: Search archived content."""
    print("\n=== Example 4: Search Archived Content ===")

    config = load_config()
    indexer = ContentIndexer(config)

    # Search for content
    query = "DAR"
    results = await indexer.search(query, limit=10)

    print(f"Found {len(results)} results for '{query}'")
    for i, result in enumerate(results[:5], 1):
        title = result.metadata.get("title", "No title")
        print(f"  {i}. {title}")

    await indexer.close()


async def example_5_discover_from_original_url():
    """Example 5: Discover all snapshots for an original URL."""
    print("\n=== Example 5: Discover Snapshots ===")

    config = load_config()
    discovery = WaybackDiscovery(config)

    # Find all snapshots of the original URL
    original_url = "http://www.dar.org.br/"
    snapshots = await discovery.find_snapshots(original_url)

    print(f"Found {len(snapshots)} snapshots for {original_url}")
    for snapshot in snapshots[:10]:  # Show first 10
        from chronos_archiver.utils import format_timestamp
        dt = format_timestamp(snapshot.timestamp)
        print(f"  - {dt.strftime('%Y-%m-%d %H:%M:%S')}: {snapshot.url}")


if __name__ == "__main__":
    # Run examples
    print("ChronosArchiver - Basic Usage Examples")
    print("=======================================")

    # Uncomment the examples you want to run:

    # asyncio.run(example_1_archive_single_url())
    # asyncio.run(example_2_archive_multiple_urls())
    # asyncio.run(example_3_manual_pipeline())
    # asyncio.run(example_4_search_archived_content())
    asyncio.run(example_5_discover_from_original_url())

    print("\n✓ Examples complete!")