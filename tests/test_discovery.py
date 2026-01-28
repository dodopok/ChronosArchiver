"""Tests for discovery module."""

import pytest
from chronos_archiver.discovery import WaybackDiscovery
from chronos_archiver.models import ArchiveSnapshot, ArchiveStatus


@pytest.mark.asyncio
async def test_parse_wayback_url():
    """Test parsing Wayback Machine URLs."""
    discovery = WaybackDiscovery()

    url = "https://web.archive.org/web/20090430060114/http://www.dar.org.br/"
    snapshots = await discovery.find_snapshots(url)

    assert len(snapshots) == 1
    assert snapshots[0].timestamp == "20090430060114"
    assert snapshots[0].original_url == "http://www.dar.org.br/"
    assert snapshots[0].status == ArchiveStatus.DISCOVERED


@pytest.mark.asyncio
async def test_create_snapshot_from_wayback_url():
    """Test creating snapshot from Wayback URL."""
    discovery = WaybackDiscovery()

    url = "https://web.archive.org/web/20120302052501/http://www.dar.org.br/"
    snapshot = await discovery._create_snapshot_from_wayback_url(url)

    assert snapshot.url == url
    assert snapshot.timestamp == "20120302052501"
    assert snapshot.original_url == "http://www.dar.org.br/"


@pytest.mark.asyncio
async def test_batch_discover():
    """Test batch discovery."""
    discovery = WaybackDiscovery()

    urls = [
        "https://web.archive.org/web/20090430060114/http://www.dar.org.br/",
        "https://web.archive.org/web/20120302052501/http://www.dar.org.br/",
    ]

    snapshots = await discovery.batch_discover(urls)

    assert len(snapshots) >= 2