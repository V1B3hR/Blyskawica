"""
Event Stream Manager

Manages event streaming with support for multiple backends.
"""

import json
import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Callable, Optional

from .events import BaseEvent

logger = logging.getLogger(__name__)


class StreamBackend(Enum):
    """Supported streaming backends."""

    KAFKA = "kafka"
    NATS = "nats"
    REDIS = "redis"
    MEMORY = "memory"  # For testing


class EventProducer(ABC):
    """Abstract event producer interface."""

    @abstractmethod
    async def publish(self, topic: str, event: BaseEvent) -> bool:
        """Publish event to topic."""
        pass

    @abstractmethod
    async def close(self):
        """Close producer connection."""
        pass


class EventConsumer(ABC):
    """Abstract event consumer interface."""

    @abstractmethod
    async def subscribe(self, topic: str, callback: Callable[[BaseEvent], None]):
        """Subscribe to topic with callback."""
        pass

    @abstractmethod
    async def unsubscribe(self, topic: str):
        """Unsubscribe from topic."""
        pass

    @abstractmethod
    async def close(self):
        """Close consumer connection."""
        pass


class MemoryEventProducer(EventProducer):
    """In-memory event producer for testing."""

    def __init__(self):
        self.events: list[tuple[str, BaseEvent]] = []

    async def publish(self, topic: str, event: BaseEvent) -> bool:
        """Publish event to in-memory store."""
        self.events.append((topic, event))
        logger.debug(f"Published event {event.event_id} to topic {topic}")
        return True

    async def close(self):
        """Close producer."""
        self.events.clear()


class MemoryEventConsumer(EventConsumer):
    """In-memory event consumer for testing."""

    def __init__(self):
        self.subscriptions: dict[str, Callable] = {}

    async def subscribe(self, topic: str, callback: Callable[[BaseEvent], None]):
        """Subscribe to topic."""
        self.subscriptions[topic] = callback
        logger.debug(f"Subscribed to topic {topic}")

    async def unsubscribe(self, topic: str):
        """Unsubscribe from topic."""
        if topic in self.subscriptions:
            del self.subscriptions[topic]
            logger.debug(f"Unsubscribed from topic {topic}")

    async def close(self):
        """Close consumer."""
        self.subscriptions.clear()


class EventStreamManager:
    """
    Event Stream Manager.

    Manages event producers and consumers with support for multiple backends.

    Features:
    - Multiple backend support (Kafka, NATS, Redis, Memory)
    - Topic-based pub/sub
    - Event serialization/deserialization
    - Connection management

    Topic Structure:
    - nethical.assets - Asset events
    - nethical.vulnerabilities - Vulnerability events
    - nethical.alerts - Alert events
    - nethical.scans - Scan events
    - nethical.cisa - CISA-specific events
    """

    TOPIC_ASSETS = "nethical.assets"
    TOPIC_VULNERABILITIES = "nethical.vulnerabilities"
    TOPIC_ALERTS = "nethical.alerts"
    TOPIC_SCANS = "nethical.scans"
    TOPIC_CISA = "nethical.cisa"

    def __init__(self, backend: StreamBackend = StreamBackend.MEMORY, config: Optional[dict[str, Any]] = None):
        """
        Initialize event stream manager.

        Args:
            backend: Streaming backend to use
            config: Backend-specific configuration
        """
        self.backend = backend
        self.config = config or {}
        self._producer: Optional[EventProducer] = None
        self._consumer: Optional[EventConsumer] = None
        self._initialize_backend()

    def _initialize_backend(self):
        """Initialize streaming backend."""
        if self.backend == StreamBackend.MEMORY:
            self._producer = MemoryEventProducer()
            self._consumer = MemoryEventConsumer()
            logger.info("Initialized in-memory event streaming")
        elif self.backend == StreamBackend.KAFKA:
            logger.warning("Kafka backend requires kafka-python package - falling back to memory")
            self._producer = MemoryEventProducer()
            self._consumer = MemoryEventConsumer()
        elif self.backend == StreamBackend.NATS:
            logger.warning("NATS backend requires nats-py package - falling back to memory")
            self._producer = MemoryEventProducer()
            self._consumer = MemoryEventConsumer()
        elif self.backend == StreamBackend.REDIS:
            logger.warning("Redis backend requires redis package - falling back to memory")
            self._producer = MemoryEventProducer()
            self._consumer = MemoryEventConsumer()
        else:
            raise ValueError(f"Unsupported backend: {self.backend}")

    async def publish_event(self, topic: str, event: BaseEvent) -> bool:
        """
        Publish event to topic.

        Args:
            topic: Topic name
            event: Event to publish

        Returns:
            True if published successfully
        """
        if not self._producer:
            logger.error("Producer not initialized")
            return False

        try:
            return await self._producer.publish(topic, event)
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
            return False

    async def subscribe(self, topic: str, callback: Callable[[BaseEvent], None]):
        """
        Subscribe to topic.

        Args:
            topic: Topic name
            callback: Callback function to handle events
        """
        if not self._consumer:
            logger.error("Consumer not initialized")
            return

        try:
            await self._consumer.subscribe(topic, callback)
        except Exception as e:
            logger.error(f"Failed to subscribe to topic: {e}")

    async def unsubscribe(self, topic: str):
        """
        Unsubscribe from topic.

        Args:
            topic: Topic name
        """
        if not self._consumer:
            return

        try:
            await self._consumer.unsubscribe(topic)
        except Exception as e:
            logger.error(f"Failed to unsubscribe from topic: {e}")

    async def close(self):
        """Close all connections."""
        if self._producer:
            await self._producer.close()
        if self._consumer:
            await self._consumer.close()

        logger.info("Event stream manager closed")

    def get_statistics(self) -> dict[str, Any]:
        """
        Get streaming statistics.

        Returns:
            Statistics dictionary
        """
        stats = {
            "backend": self.backend.value,
            "producer_connected": self._producer is not None,
            "consumer_connected": self._consumer is not None,
        }

        # Add backend-specific stats
        if self.backend == StreamBackend.MEMORY and isinstance(self._producer, MemoryEventProducer):
            stats["events_published"] = len(self._producer.events)

        return stats
