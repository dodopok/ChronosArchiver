"""Tests for search engine."""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from chronos_archiver.search import SearchEngine
from chronos_archiver.models import ContentAnalysis, ArchiveSnapshot, MediaEmbed


class TestSearchEngine:
    """Test SearchEngine class."""

    def test_initialization(self, test_config):
        """Test search engine initialization."""
        test_config["search"] = {
            "meilisearch_host": "http://localhost:7700",
            "index_name": "test_index"
        }
        
        with patch('meilisearch.Client') as mock_client:
            mock_index = MagicMock()
            mock_client.return_value.index.return_value = mock_index
            
            engine = SearchEngine(test_config)
            
            assert engine.index_name == "test_index"
            mock_client.assert_called_once()

    @pytest.mark.asyncio
    async def test_index_content(self, test_config, sample_snapshot):
        """Test indexing content analysis."""
        test_config["search"] = {
            "meilisearch_host": "http://localhost:7700",
            "index_name": "test_index"
        }
        
        with patch('meilisearch.Client') as mock_client:
            mock_index = MagicMock()
            mock_index.add_documents = MagicMock(return_value={"updateId": 0})
            mock_client.return_value.index.return_value = mock_index
            
            engine = SearchEngine(test_config)
            
            # Create analysis
            analysis = ContentAnalysis(
                snapshot=sample_snapshot,
                text_content="Test content about Diocese Anglicana",
                keywords=["diocese", "igreja"],
                topics=["religião"],
                languages=[("pt", 0.9)],
            )
            
            result = await engine.index_content(analysis)
            
            assert result is True
            mock_index.add_documents.assert_called_once()

    @pytest.mark.asyncio
    async def test_search(self, test_config):
        """Test search functionality."""
        test_config["search"] = {
            "meilisearch_host": "http://localhost:7700",
            "index_name": "test_index"
        }
        
        with patch('meilisearch.Client') as mock_client:
            mock_index = MagicMock()
            mock_index.search = MagicMock(return_value={
                "hits": [
                    {
                        "id": "1",
                        "url": "https://web.archive.org/web/test",
                        "original_url": "http://test.com",
                        "timestamp": "20090430060114",
                        "title": "Test Page",
                        "text_content": "Test content",
                        "keywords": ["test"],
                        "topics": ["test"],
                        "_rankingScore": 0.9,
                    }
                ],
                "estimatedTotalHits": 1,
            })
            mock_client.return_value.index.return_value = mock_index
            
            engine = SearchEngine(test_config)
            
            results = await engine.search("test query")
            
            assert len(results) == 1
            assert results[0].title == "Test Page"
            assert results[0].score == 0.9

    @pytest.mark.asyncio
    async def test_search_with_filters(self, test_config):
        """Test search with filters."""
        test_config["search"] = {
            "meilisearch_host": "http://localhost:7700",
            "index_name": "test_index"
        }
        
        with patch('meilisearch.Client') as mock_client:
            mock_index = MagicMock()
            mock_index.search = MagicMock(return_value={"hits": []})
            mock_client.return_value.index.return_value = mock_index
            
            engine = SearchEngine(test_config)
            
            filters = {
                "topics": ["religião"],
                "has_videos": True,
            }
            
            results = await engine.search("test", filters=filters)
            
            # Verify search was called with filters
            mock_index.search.assert_called_once()
            call_args = mock_index.search.call_args
            assert call_args[0][0] == "test"
            assert "filter" in call_args[1]

    @pytest.mark.asyncio
    async def test_get_suggestions(self, test_config):
        """Test search suggestions."""
        test_config["search"] = {
            "meilisearch_host": "http://localhost:7700",
            "index_name": "test_index"
        }
        
        with patch('meilisearch.Client') as mock_client:
            mock_index = MagicMock()
            mock_index.search = MagicMock(return_value={
                "hits": [
                    {"title": "Diocese Anglicana", "keywords": ["diocese", "igreja"]},
                    {"title": "Diocese Episcopal", "keywords": ["episcopal"]},
                ],
            })
            mock_client.return_value.index.return_value = mock_index
            
            engine = SearchEngine(test_config)
            
            suggestions = await engine.suggest("dio", limit=5)
            
            assert len(suggestions) > 0
            assert any("diocese" in s.lower() for s in suggestions)