"""Tests for FastAPI web interface."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from chronos_archiver.api import app


class TestAPI:
    """Test FastAPI endpoints."""

    def test_health_check(self):
        """Test health check endpoint."""
        client = TestClient(app)
        
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"

    def test_home_page(self):
        """Test home page endpoint."""
        client = TestClient(app)
        
        response = client.get("/")
        
        assert response.status_code == 200
        assert "ChronosArchiver" in response.text
        assert "Diocese" in response.text or "Busca" in response.text

    @pytest.mark.asyncio
    async def test_search_endpoint(self):
        """Test search API endpoint."""
        client = TestClient(app)
        
        with patch('chronos_archiver.api.search_engine') as mock_search:
            mock_search.search = AsyncMock(return_value=[])
            
            response = client.get("/api/search?q=diocese")
            
            # Note: This will fail without proper async setup in TestClient
            # This is a placeholder test structure

    def test_api_docs_available(self):
        """Test that API documentation is available."""
        client = TestClient(app)
        
        response = client.get("/api/docs")
        
        # Should redirect or show docs
        assert response.status_code in [200, 307]