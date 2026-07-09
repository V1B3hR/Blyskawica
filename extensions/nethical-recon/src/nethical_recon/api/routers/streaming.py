"""
Streaming API Router

FastAPI router for event streaming endpoints.
"""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from nethical_recon.streaming import EventStreamManager
from nethical_recon.streaming.manager import StreamBackend

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/streaming", tags=["streaming"])

# Initialize event stream manager (in-memory for now)
stream_manager = EventStreamManager(backend=StreamBackend.MEMORY)


# Request/Response Models


class PublishEventRequest(BaseModel):
    """Request to publish an event."""

    topic: str = Field(..., description="Topic name (nethical.assets, nethical.vulnerabilities, etc.)")
    event_type: str = Field(..., description="Event type")
    event_data: dict[str, Any] = Field(..., description="Event data")


class SubscribeRequest(BaseModel):
    """Request to subscribe to a topic."""

    topic: str = Field(..., description="Topic name")
    callback_url: str = Field(..., description="Webhook URL for event callbacks")


# Streaming Endpoints


@router.get("/topics")
async def list_topics():
    """List available event streaming topics."""
    topics = [
        {
            "topic": EventStreamManager.TOPIC_ASSETS,
            "description": "Asset discovery and updates",
            "event_types": ["asset_discovered"],
        },
        {
            "topic": EventStreamManager.TOPIC_VULNERABILITIES,
            "description": "Vulnerability findings",
            "event_types": ["vulnerability_found"],
        },
        {
            "topic": EventStreamManager.TOPIC_ALERTS,
            "description": "Security alerts and notifications",
            "event_types": ["alert_generated"],
        },
        {
            "topic": EventStreamManager.TOPIC_SCANS,
            "description": "Scan completions and results",
            "event_types": ["scan_completed"],
        },
        {
            "topic": EventStreamManager.TOPIC_CISA,
            "description": "CISA-specific events (KEV, alerts, Shields Up)",
            "event_types": ["cisa_alert_received"],
        },
    ]

    return {"success": True, "data": topics}


@router.get("/statistics")
async def get_streaming_statistics():
    """Get event streaming statistics."""
    try:
        stats = stream_manager.get_statistics()
        return {"success": True, "data": stats}
    except Exception as e:
        logger.error(f"Failed to get streaming statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/publish")
async def publish_event(request: PublishEventRequest):
    """
    Publish event to topic.

    Note: This is a simplified implementation.
    In production, events would be published internally by the system.
    """
    try:
        # This is a simplified demonstration
        logger.info(f"Event publish requested for topic {request.topic}")

        return {
            "success": True,
            "message": f"Event published to {request.topic}",
            "data": {
                "topic": request.topic,
                "event_type": request.event_type,
            },
        }
    except Exception as e:
        logger.error(f"Failed to publish event: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/subscribe")
async def subscribe_to_topic(request: SubscribeRequest):
    """
    Subscribe to event topic.

    Note: This is a simplified implementation.
    In production, this would set up webhooks or WebSocket connections.
    """
    try:
        logger.info(f"Subscription requested for topic {request.topic}")

        return {
            "success": True,
            "message": f"Subscribed to {request.topic}",
            "data": {
                "topic": request.topic,
                "callback_url": request.callback_url,
                "subscription_id": "sub-demo-12345",
            },
        }
    except Exception as e:
        logger.error(f"Failed to subscribe to topic: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/backends")
async def list_backends():
    """List available streaming backends."""
    backends = [
        {
            "backend": "memory",
            "name": "In-Memory",
            "description": "In-memory event storage for testing",
            "status": "available",
        },
        {
            "backend": "kafka",
            "name": "Apache Kafka",
            "description": "Distributed streaming platform",
            "status": "requires kafka-python package",
        },
        {
            "backend": "nats",
            "name": "NATS",
            "description": "Cloud native messaging system",
            "status": "requires nats-py package",
        },
        {
            "backend": "redis",
            "name": "Redis Streams",
            "description": "Redis-based event streaming",
            "status": "requires redis package",
        },
    ]

    return {"success": True, "data": backends}


@router.get("/health")
async def check_streaming_health():
    """Check streaming system health."""
    try:
        stats = stream_manager.get_statistics()

        health = {
            "healthy": stats["producer_connected"] and stats["consumer_connected"],
            "backend": stats["backend"],
            "producer_status": "connected" if stats["producer_connected"] else "disconnected",
            "consumer_status": "connected" if stats["consumer_connected"] else "disconnected",
        }

        return {"success": True, "data": health}
    except Exception as e:
        logger.error(f"Failed to check streaming health: {e}")
        raise HTTPException(status_code=500, detail=str(e))
