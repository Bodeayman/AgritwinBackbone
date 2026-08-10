import asyncio
from aio_pika import connect_robust, Message, ExchangeType
from app.core.config import Settings, get_settings

class ImageProcessingService:
    """Service to enqueue image URLs for asynchronous AI processing via RabbitMQ."""
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        self._connection = None
        self._channel = None
        self._exchange = None
        self._loop = asyncio.get_event_loop()
        # Initialize connection lazily
        self._loop.create_task(self._initialize())

    async def _initialize(self):
        """Establish connection and declare exchange/queue."""
        self._connection = await connect_robust(self.settings.RABBITMQ_URL)
        self._channel = await self._connection.channel()
        # Direct exchange for simplicity
        self._exchange = await self._channel.declare_exchange(
            "agri_image_exchange", type=ExchangeType.DIRECT, durable=True
        )
        # Declare queue (idempotent)
        await self._channel.declare_queue(
            "agri_image_tasks", durable=True
        )

    async def enqueue_image(self, image_url: str) -> None:
        """Publish a message containing the image URL to the processing queue.

        The consumer (worker) will later fetch the URL, download the image, run the
        AI model and store the results.
        """
        if self._exchange is None:
            # Ensure connection is ready
            await self._initialize()
        payload = image_url.encode()
        message = Message(payload, delivery_mode=2)  # persistent
        await self._exchange.publish(message, routing_key="agri_image_tasks")
        # For debugging, you may log the publish action.
        print(f"[ImageProcessingService] Enqueued image URL: {image_url}")
