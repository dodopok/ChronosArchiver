"""Tests for queue manager module."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from chronos_archiver.queue_manager import QueueManager
from chronos_archiver.models import QueueMessage


class TestQueueManager:
    """Test QueueManager class."""

    @pytest.mark.asyncio
    async def test_connect_redis(self, test_config):
        """Test connecting to Redis."""
        queue_manager = QueueManager(test_config)
        
        with patch('redis.asyncio.from_url') as mock_redis:
            mock_client = AsyncMock()
            mock_redis.return_value = mock_client
            
            await queue_manager.connect()
            
            assert queue_manager.redis_client is not None
            mock_redis.assert_called_once()

    @pytest.mark.asyncio
    async def test_enqueue_message(self, test_config):
        """Test enqueueing a message."""
        queue_manager = QueueManager(test_config)
        
        with patch('redis.asyncio.from_url') as mock_redis:
            mock_client = AsyncMock()
            mock_client.rpush = AsyncMock(return_value=1)
            mock_redis.return_value = mock_client
            
            await queue_manager.connect()
            message_id = await queue_manager.enqueue(
                "discovery",
                "snapshot",
                {"url": "http://example.com"}
            )
            
            assert message_id is not None
            mock_client.rpush.assert_called_once()

    @pytest.mark.asyncio
    async def test_dequeue_message(self, test_config):
        """Test dequeuing a message."""
        queue_manager = QueueManager(test_config)
        
        import json
        test_message = QueueMessage(
            id="test-123",
            type="snapshot",
            payload={"url": "http://example.com"}
        )
        
        with patch('redis.asyncio.from_url') as mock_redis:
            mock_client = AsyncMock()
            mock_client.lpop = AsyncMock(
                return_value=json.dumps(test_message.model_dump(), default=str)
            )
            mock_redis.return_value = mock_client
            
            await queue_manager.connect()
            message = await queue_manager.dequeue("discovery")
            
            assert message is not None
            assert message.id == "test-123"
            assert message.type == "snapshot"

    @pytest.mark.asyncio
    async def test_queue_size(self, test_config):
        """Test getting queue size."""
        queue_manager = QueueManager(test_config)
        
        with patch('redis.asyncio.from_url') as mock_redis:
            mock_client = AsyncMock()
            mock_client.llen = AsyncMock(return_value=5)
            mock_redis.return_value = mock_client
            
            await queue_manager.connect()
            size = await queue_manager.queue_size("discovery")
            
            assert size == 5

    @pytest.mark.asyncio
    async def test_clear_queue(self, test_config):
        """Test clearing a queue."""
        queue_manager = QueueManager(test_config)
        
        with patch('redis.asyncio.from_url') as mock_redis:
            mock_client = AsyncMock()
            mock_client.delete = AsyncMock(return_value=1)
            mock_redis.return_value = mock_client
            
            await queue_manager.connect()
            await queue_manager.clear_queue("discovery")
            
            mock_client.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_disconnect(self, test_config):
        """Test disconnecting from queue backend."""
        queue_manager = QueueManager(test_config)
        
        with patch('redis.asyncio.from_url') as mock_redis:
            mock_client = AsyncMock()
            mock_client.close = AsyncMock()
            mock_redis.return_value = mock_client
            
            await queue_manager.connect()
            await queue_manager.disconnect()
            
            mock_client.close.assert_called_once()