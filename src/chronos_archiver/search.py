"""Search module - Advanced search with Meilisearch integration."""

import logging
from datetime import datetime
from typing import Any, Optional

import meilisearch
from meilisearch.errors import MeilisearchApiError

from chronos_archiver.models import ContentAnalysis, SearchResult

logger = logging.getLogger(__name__)


class SearchEngine:
    """Motor de busca avançado com Meilisearch.
    
    Advanced search engine with:
    - Full-text search
    - Faceted search
    - Typo tolerance
    - Ranking and relevance
    - Filtering and sorting
    - Brazilian Portuguese support
    """

    def __init__(self, config: Optional[dict] = None) -> None:
        """Initialize search engine.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        search_config = self.config.get("search", {})
        
        self.host = search_config.get("meilisearch_host", "http://localhost:7700")
        self.api_key = search_config.get("meilisearch_api_key")
        self.index_name = search_config.get("index_name", "chronos_archive")
        
        # Connect to Meilisearch
        self.client = meilisearch.Client(self.host, self.api_key)
        self.index = None
        
        self._setup_index()

    def _setup_index(self) -> None:
        """Setup Meilisearch index with configuration."""
        try:
            # Create or get index
            self.index = self.client.index(self.index_name)
            
            # Configure searchable attributes
            self.index.update_searchable_attributes([
                "title",
                "text_content",
                "url",
                "original_url",
                "keywords",
                "entities",
                "summary",
            ])
            
            # Configure filterable attributes
            self.index.update_filterable_attributes([
                "timestamp",
                "mime_type",
                "languages",
                "topics",
                "has_images",
                "has_videos",
                "platform",
            ])
            
            # Configure sortable attributes
            self.index.update_sortable_attributes([
                "timestamp",
                "word_count",
            ])
            
            # Configure ranking rules
            self.index.update_ranking_rules([
                "words",
                "typo",
                "proximity",
                "attribute",
                "sort",
                "exactness",
            ])
            
            # Configure typo tolerance for Portuguese
            self.index.update_typo_tolerance({
                "enabled": True,
                "minWordSizeForTypos": {
                    "oneTypo": 4,
                    "twoTypos": 8,
                },
            })
            
            logger.info(f"Meilisearch index '{self.index_name}' configured")
            
        except MeilisearchApiError as e:
            logger.error(f"Failed to setup Meilisearch index: {e}")
            raise

    async def index_content(self, analysis: ContentAnalysis) -> bool:
        """Index content analysis in search engine.
        
        Args:
            analysis: Content analysis to index
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Prepare document for indexing
            doc = {
                "id": f"{analysis.snapshot.timestamp}_{hash(analysis.snapshot.url)}",
                "url": analysis.snapshot.url,
                "original_url": analysis.snapshot.original_url,
                "timestamp": analysis.snapshot.timestamp,
                "title": analysis.metadata.get("title", ""),
                "text_content": analysis.text_content[:100000],  # Limit size
                "keywords": analysis.keywords,
                "entities": self._flatten_entities(analysis.entities),
                "topics": analysis.topics,
                "languages": [lang for lang, _ in analysis.languages],
                "mime_type": analysis.snapshot.mime_type,
                "has_images": analysis.has_images,
                "has_videos": analysis.has_videos,
                "word_count": analysis.word_count,
                "summary": analysis.summary,
                "media_embeds": [
                    {
                        "type": embed.type,
                        "platform": embed.platform,
                        "url": embed.url,
                        "video_id": embed.video_id,
                    }
                    for embed in analysis.media_embeds
                ],
            }
            
            # Add to index
            self.index.add_documents([doc])
            
            logger.info(f"Indexed content: {analysis.snapshot.url}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to index content: {e}")
            return False

    def _flatten_entities(self, entities: dict[str, list[str]]) -> list[str]:
        """Flatten entity dictionary to list.
        
        Args:
            entities: Dictionary of entity types to lists
            
        Returns:
            Flattened list of entities
        """
        flattened = []
        for entity_list in entities.values():
            flattened.extend(entity_list)
        return flattened

    async def search(
        self,
        query: str,
        filters: Optional[dict[str, Any]] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[SearchResult]:
        """Search indexed content.
        
        Args:
            query: Search query
            filters: Optional filters (e.g., {"topics": "religião"})
            limit: Maximum results
            offset: Result offset for pagination
            
        Returns:
            List of search results
        """
        try:
            # Build filter string
            filter_str = None
            if filters:
                filter_parts = []
                for key, value in filters.items():
                    if isinstance(value, list):
                        filter_parts.append(f"{key} IN {value}")
                    else:
                        filter_parts.append(f"{key} = '{value}'")
                filter_str = " AND ".join(filter_parts)
            
            # Search
            results = self.index.search(
                query,
                {
                    "limit": limit,
                    "offset": offset,
                    "filter": filter_str,
                    "attributesToHighlight": ["title", "text_content"],
                    "highlightPreTag": "<mark>",
                    "highlightPostTag": "</mark>",
                }
            )
            
            # Convert to SearchResult objects
            search_results = []
            for hit in results["hits"]:
                result = SearchResult(
                    id=hit["id"],
                    url=hit["url"],
                    original_url=hit["original_url"],
                    timestamp=hit["timestamp"],
                    title=hit.get("title", ""),
                    snippet=self._generate_snippet(hit.get("text_content", ""), query),
                    highlights=hit.get("_formatted", {}),
                    score=hit.get("_rankingScore", 0),
                    keywords=hit.get("keywords", []),
                    topics=hit.get("topics", []),
                    has_videos=hit.get("has_videos", False),
                    media_embeds=hit.get("media_embeds", []),
                )
                search_results.append(result)
            
            logger.info(f"Search '{query}' returned {len(search_results)} results")
            return search_results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def _generate_snippet(self, text: str, query: str, max_length: int = 200) -> str:
        """Generate a snippet around search query.
        
        Args:
            text: Full text
            query: Search query
            max_length: Maximum snippet length
            
        Returns:
            Text snippet
        """
        if not text:
            return ""
        
        # Find query position
        text_lower = text.lower()
        query_lower = query.lower()
        pos = text_lower.find(query_lower)
        
        if pos == -1:
            # Query not found, return beginning
            return text[:max_length] + "..." if len(text) > max_length else text
        
        # Extract snippet around query
        start = max(0, pos - max_length // 2)
        end = min(len(text), pos + len(query) + max_length // 2)
        
        snippet = text[start:end]
        
        if start > 0:
            snippet = "..." + snippet
        if end < len(text):
            snippet = snippet + "..."
        
        return snippet

    async def get_facets(self) -> dict[str, Any]:
        """Get facet counts for filtering.
        
        Returns:
            Dictionary of facet counts
        """
        try:
            # Get facet distribution
            results = self.index.search(
                "",
                {
                    "facets": ["topics", "languages", "mime_type", "has_videos"],
                }
            )
            
            return results.get("facetDistribution", {})
            
        except Exception as e:
            logger.error(f"Failed to get facets: {e}")
            return {}

    async def suggest(self, query: str, limit: int = 5) -> list[str]:
        """Get search suggestions.
        
        Args:
            query: Partial query
            limit: Maximum suggestions
            
        Returns:
            List of suggestions
        """
        try:
            results = self.index.search(
                query,
                {
                    "limit": limit,
                    "attributesToRetrieve": ["title", "keywords"],
                }
            )
            
            suggestions = set()
            for hit in results["hits"]:
                if hit.get("title"):
                    suggestions.add(hit["title"])
                for keyword in hit.get("keywords", [])[:3]:
                    suggestions.add(keyword)
            
            return list(suggestions)[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get suggestions: {e}")
            return []