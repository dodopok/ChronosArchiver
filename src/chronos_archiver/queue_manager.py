"""Queue manager for async pipeline processing."""

import asyncio
import json
import logging
from typing import Any, Callable, Optional
from uuid import uuid4

import redis.asyncio as aioredis

from chronos_archiver.models import QueueMessage

logger = logging.getLogger(__name__)


class QueueManager:
    """Manage message queues for async processing."""

    def __init__(self, config: Optional[dict] = None) -> None:
        """Initialize queue manager.

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        queue_config = self.config.get("queue", {})

        self.backend = queue_config.get("backend", "redis")
        self.redis_url = queue_config.get("redis_url", "redis://localhost:6379/0")

        self.queue_names = {
            "discovery": queue_config.get("discovery_queue", "chronos:discovery"),
            "ingestion": queue_config.get("ingestion_queue", "chronos:ingestion"),
            "transformation": queue_config.get("transformation_queue", "chronos:transformation"),
            "indexing": queue_config.get("indexing_queue", "chronos:indexing"),
        }

        self.redis_client = None
        self.workers = []
        self.running = False

    async def connect(self) -> None:
        """Connect to queue backend."""
        if self.backend == "redis":
            self.redis_client = await aioredis.from_url(self.redis_url, decode_responses=True)
            logger.info(f"Connected to Redis: {self.redis_url}")
        else:
            raise ValueError(f"Unsupported queue backend: {self.backend}")

    async def disconnect(self) -> None:
        """Disconnect from queue backend."""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Disconnected from queue backend")

    async def enqueue(
        self, queue_name: str, message_type: str, payload: dict[str, Any]
    ) -> str:
        """Add a message to a queue.

        Args:
            queue_name: Name of the queue
            message_type: Type of message
            payload: Message payload

        Returns:
            Message ID
        """
        if not self.redis_client:
            await self.connect()

        message = QueueMessage(
            id=str(uuid4()), type=message_type, payload=payload
        )

        full_queue_name = self.queue_names.get(queue_name, queue_name)

        # Push to Redis list
        await self.redis_client.rpush(
            full_queue_name, json.dumps(message.model_dump(), default=str)
        )

        logger.debug(f"Enqueued message {message.id} to {full_queue_name}")
        return message.id

    async def dequeue(self, queue_name: str, timeout: int = 0) -> Optional[QueueMessage]:
        """Remove and return a message from a queue.

        Args:
            queue_name: Name of the queue
            timeout: Blocking timeout in seconds (0 = non-blocking)

        Returns:
            Message or None if queue is empty
        """
        if not self.redis_client:
            await self.connect()

        full_queue_name = self.queue_names.get(queue_name, queue_name)

        if timeout > 0:
            result = await self.redis_client.blpop(full_queue_name, timeout=timeout)
            if result:
                _, message_json = result
            else:
                return None
        else:
            message_json = await self.redis_client.lpop(full_queue_name)

        if not message_json:
            return None

        message_data = json.loads(message_json)
        return QueueMessage(**message_data)

    async def start_workers(
        self, worker_count: int, handler: Optional[Callable] = None
    ) -> None:
        """Start background workers.

        Args:
            worker_count: Number of workers to start
            handler: Optional message handler function
        """
        self.running = True

        for i in range(worker_count):
            worker = asyncio.create_task(self._worker(i, handler))
            self.workers.append(worker)

        logger.info(f"Started {worker_count} workers")

    async def _worker(self, worker_id: int, handler: Optional[Callable] = None) -> None:
        """Worker task that processes messages.

        Args:
            worker_id: Worker identifier
            handler: Message handler function
        """
        logger.info(f"Worker {worker_id} started")

        while self.running:
            try:
                # Process each queue in order
                for queue_name in ["discovery", "ingestion", "transformation", "indexing"]:
                    message = await self.dequeue(queue_name, timeout=1)

                    if message and handler:
                        try:
                            await handler(queue_name, message)
                        except Exception as e:
                            logger.error(
                                f"Worker {worker_id} error processing message {message.id}: {e}"
                            )
                            # Re-queue if retry count is below threshold
                            if message.retry_count < 3:
                                message.retry_count += 1
                                await self.enqueue(
                                    queue_name, message.type, message.payload
                                )

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
                await asyncio.sleep(1)

        logger.info(f"Worker {worker_id} stopped")

    async def shutdown(self) -> None:
        """Shutdown all workers and disconnect."""
        logger.info("Shutting down queue manager...")
        self.running = False

        # Cancel all workers
        for worker in self.workers:
            worker.cancel()

        # Wait for workers to finish
        await asyncio.gather(*self.workers, return_exceptions=True)

        # Disconnect
        await self.disconnect()

        logger.info("Queue manager shutdown complete")

    async def queue_size(self, queue_name: str) -> int:
        """Get the size of a queue.

        Args:
            queue_name: Name of the queue

        Returns:
            Number of messages in queue
        """
        if not self.redis_client:
            await self.connect()

        full_queue_name = self.queue_names.get(queue_name, queue_name)
        return await self.redis_client.llen(full_queue_name)

    async def clear_queue(self, queue_name: str) -> None:
        """Clear all messages from a queue.

        Args:
            queue_name: Name of the queue
        """
        if not self.redis_client:
            await self.connect()

        full_queue_name = self.queue_names.get(queue_name, queue_name)
        await self.redis_client.delete(full_queue_name)
        logger.info(f"Cleared queue: {full_queue_name}")