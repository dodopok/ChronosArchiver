#!/usr/bin/env python
"""Basic usage examples for ChronosArchiver."""

import asyncio
from chronos_archiver import ChronosArchiver
from chronos_archiver.config import load_config


async def archive_single_url():
    """Example: Archive a single URL."""
    print("Example 1: Archive a single URL")
    print("=" * 50)
    
    config = load_config()
    archiver = ChronosArchiver(config)
    
    url = "https://web.archive.org/web/20090430060114/http://www.dar.org.br/"
    
    print(f"Archiving: {url}")
    await archiver.archive_url(url)
    
    print("\n✓ Archive complete!\n")
    await archiver.shutdown()


async def archive_multiple_urls():
    """Example: Archive multiple URLs."""
    print("Example 2: Archive multiple URLs")
    print("=" * 50)
    
    config = load_config()
    archiver = ChronosArchiver(config)
    
    urls = [
        "https://web.archive.org/web/20090430060114/http://www.dar.org.br/",
        "https://web.archive.org/web/20120302052501/http://www.dar.org.br/",
        "https://web.archive.org/web/20150406103050/http://dar.org.br/",
    ]
    
    print(f"Archiving {len(urls)} URLs...")
    await archiver.archive_urls(urls)
    
    print("\n✓ All archives complete!\n")
    await archiver.shutdown()


async def discover_and_archive():
    """Example: Discover all snapshots for a URL and archive them."""
    print("Example 3: Discover and archive all snapshots")
    print("=" * 50)
    
    config = load_config()
    archiver = ChronosArchiver(config)
    
    # Discover all snapshots
    print("Discovering snapshots for http://www.dar.org.br/...")
    snapshots = await archiver.discovery.find_snapshots("http://www.dar.org.br/")
    
    print(f"Found {len(snapshots)} snapshots")
    
    # Archive each snapshot
    for i, snapshot in enumerate(snapshots[:5], 1):  # Limit to first 5
        print(f"\n[{i}/{min(5, len(snapshots))}] Archiving: {snapshot.timestamp}")
        
        # Download
        content = await archiver.ingestion.download(snapshot)
        if not content:
            print("  ✗ Download failed")
            continue
        
        # Transform
        transformed = await archiver.transformation.transform(content)
        if not transformed:
            print("  ✗ Transformation failed")
            continue
        
        # Index
        indexed = await archiver.indexer.index(transformed)
        if indexed:
            print(f"  ✓ Successfully archived: {transformed.metadata.get('title', 'No title')}")
    
    print("\n✓ Discovery and archival complete!\n")
    await archiver.shutdown()


async def search_archived_content():
    """Example: Search archived content."""
    print("Example 4: Search archived content")
    print("=" * 50)
    
    config = load_config()
    archiver = ChronosArchiver(config)
    
    # Search for content
    query = "Diocese Anglicana"
    print(f"Searching for: '{query}'")
    
    results = await archiver.indexer.search(query, limit=10)
    
    print(f"\nFound {len(results)} results:\n")
    for i, result in enumerate(results, 1):
        title = result.metadata.get("title", "No title")
        print(f"{i}. {title}")
        if result.text_content:
            preview = result.text_content[:100] + "..."
            print(f"   {preview}\n")
    
    await archiver.shutdown()


async def main():
    """Run all examples."""
    examples = [
        archive_single_url,
        archive_multiple_urls,
        discover_and_archive,
        search_archived_content,
    ]
    
    print("\n" + "=" * 60)
    print("ChronosArchiver - Basic Usage Examples")
    print("=" * 60 + "\n")
    
    for i, example in enumerate(examples, 1):
        print(f"\nRunning example {i}/{len(examples)}...\n")
        try:
            await example()
        except Exception as e:
            print(f"\n✗ Example failed: {e}\n")
        
        if i < len(examples):
            input("Press Enter to continue to next example...")
    
    print("\n" + "=" * 60)
    print("All examples complete!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())