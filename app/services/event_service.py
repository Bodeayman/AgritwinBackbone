import json
import asyncio
from typing import Any, Dict

# Simple in-memory event publisher (placeholder). In production you would use aio_pika to publish to RabbitMQ.
class EventService:
    def __init__(self):
        self._queue: asyncio.Queue[Dict[str, Any]] = asyncio.Queue()

    async def publish_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        message = {"type": event_type, "payload": payload}
        # In real implementation, you would serialize and send to RabbitMQ.
        await self._queue.put(message)
        print(f"[EventService] Published event: {json.dumps(message)}")

    # Helper to retrieve messages for testing (not part of production API)
    async def get_next_event(self) -> Dict[str, Any]:
        return await self._queue.get()
