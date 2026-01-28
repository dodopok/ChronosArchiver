#!/usr/bin/env python
"""Advanced usage examples for ChronosArchiver."""

import asyncio
from pathlib import Path
from chronos_archiver import ChronosArchiver
from chronos_archiver.config import load_config
from chronos_archiver.models import ProcessingStats
import logging

logging.basicConfig(level=logging.INFO)


async def batch_archiving_with_progress():
    """Example: Batch archiving with progress tracking."""
    print("Example 1: Batch archiving with progress tracking")
    print("=" * 50)
    
    config = load_config()
    archiver = ChronosArchiver(config)
    
    # Load URLs from file
    urls_file = Path("examples/sample_sites.txt")
    urls = []
    
    if urls_file.exists():
        with open(urls_file) as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    
    print(f"Loaded {len(urls)} URLs from {urls_file}")
    
    # Track statistics
    stats = ProcessingStats(total_snapshots=len(urls))
    
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] Processing: {url}")
        
        try:
            # Discover
            snapshots = await archiver.discovery.find_snapshots(url)
            stats.discovered += len(snapshots)
            
            for snapshot in snapshots[:1]:  # Process first snapshot only
                # Download
                content = await archiver.ingestion.download(snapshot)
                if content:
                    stats.downloaded += 1
                    
                    # Transform
                    transformed = await archiver.transformation.transform(content)
                    if transformed:
                        stats.transformed += 1
                        
                        # Index
                        indexed = await archiver.indexer.index(transformed)
                        if indexed:
                            stats.indexed += 1
                            print(f"  ✓ Success: {transformed.metadata.get('title', 'No title')}")
                    else:
                        stats.failed += 1
                else:
                    stats.failed += 1
        except Exception as e:
            print(f"  ✗ Error: {e}")
            stats.failed += 1
    
    # Print final statistics
    print("\n" + "=" * 50)
    print("Processing Statistics:")
    print(f"  Total URLs: {stats.total_snapshots}")
    print(f"  Discovered: {stats.discovered}")
    print(f"  Downloaded: {stats.downloaded}")
    print(f"  Transformed: {stats.transformed}")
    print(f"  Indexed: {stats.indexed}")
    print(f"  Failed: {stats.failed}")
    print(f"  Success Rate: {stats.success_rate:.1f}%")
    print("=" * 50)
    
    await archiver.shutdown()


async def custom_transformation():
    """Example: Custom content transformation."""
    print("\nExample 2: Custom content transformation")
    print("=" * 50)
    
    config = load_config()
    
    # Customize transformation settings
    config["transformation"]["remove_scripts"] = True
    config["transformation"]["remove_comments"] = True
    config["transformation"]["extract_text"] = True
    
    archiver = ChronosArchiver(config)
    
    url = "https://web.archive.org/web/20090430060114/http://www.dar.org.br/"
    
    snapshots = await archiver.discovery.find_snapshots(url)
    if not snapshots:
        print("No snapshots found")
        return
    
    snapshot = snapshots[0]
    content = await archiver.ingestion.download(snapshot)
    
    if content:
        transformed = await archiver.transformation.transform(content)
        
        if transformed:
            print(f"\nTransformed content:")
            print(f"  Title: {transformed.metadata.get('title')}")
            print(f"  Links found: {len(transformed.links)}")
            print(f"  Text length: {len(transformed.text_content or '')} characters")
            print(f"  Metadata: {list(transformed.metadata.keys())}")
    
    await archiver.shutdown()


async def parallel_processing():
    """Example: Parallel processing with multiple workers."""
    print("\nExample 3: Parallel processing")
    print("=" * 50)
    
    config = load_config()
    config["processing"]["workers"] = 4
    config["processing"]["concurrent_requests"] = 10
    
    archiver = ChronosArchiver(config)
    
    urls = [
        "https://web.archive.org/web/20090430060114/http://www.dar.org.br/",
        "https://web.archive.org/web/20120302052501/http://www.dar.org.br/",
        "https://web.archive.org/web/20150406103050/http://dar.org.br/",
    ]
    
    print(f"Processing {len(urls)} URLs in parallel...")
    
    # Process all URLs concurrently
    await archiver.archive_urls(urls)
    
    print("\n✓ Parallel processing complete!")
    await archiver.shutdown()


async def filtered_discovery():
    """Example: Discovery with filtering."""
    print("\nExample 4: Filtered discovery")
    print("=" * 50)
    
    config = load_config()
    
    # Only get successful responses
    config["discovery"]["filter_status_codes"] = [200]
    # Enable deduplication
    config["discovery"]["deduplicate_snapshots"] = True
    
    archiver = ChronosArchiver(config)
    
    print("Discovering snapshots with filters:")
    print("  - Status codes: 200 only")
    print("  - Deduplication: enabled\n")
    
    snapshots = await archiver.discovery.find_snapshots("http://www.dar.org.br/")
    
    print(f"\nFound {len(snapshots)} unique snapshots:")
    for snapshot in snapshots[:10]:  # Show first 10
        print(f"  - {snapshot.timestamp}: {snapshot.original_url}")
    
    await archiver.shutdown()


async def export_to_warc():
    """Example: Export archived content (placeholder for WARC export)."""
    print("\nExample 5: Export functionality")
    print("=" * 50)
    
    config = load_config()
    archiver = ChronosArchiver(config)
    
    print("Searching for archived content...")
    results = await archiver.indexer.search("Diocese", limit=5)
    
    print(f"\nFound {len(results)} archived pages")
    print("\nNote: WARC export is planned for future release")
    print("Current exports available:")
    print("  - HTML files (organized by date)")
    print("  - SQLite database with metadata")
    print("  - Full-text search index")
    
    await archiver.shutdown()


async def main():
    """Run all advanced examples."""
    examples = [
        batch_archiving_with_progress,
        custom_transformation,
        parallel_processing,
        filtered_discovery,
        export_to_warc,
    ]
    
    print("\n" + "=" * 60)
    print("ChronosArchiver - Advanced Usage Examples")
    print("=" * 60 + "\n")
    
    for i, example in enumerate(examples, 1):
        print(f"\nRunning example {i}/{len(examples)}...\n")
        try:
            await example()
        except Exception as e:
            print(f"\n✗ Example failed: {e}\n")
            import traceback
            traceback.print_exc()
        
        if i < len(examples):
            input("\nPress Enter to continue to next example...")
    
    print("\n" + "=" * 60)
    print("All examples complete!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())