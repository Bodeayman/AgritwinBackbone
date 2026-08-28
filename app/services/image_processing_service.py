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

    async def _initialize(self):
        """Establish connection and declare exchange/queue."""

        self._connection = await connect_robust(
            self.settings.RABBITMQ_URL
        )

        self._channel = await self._connection.channel()

        self._exchange = await self._channel.declare_exchange(
            "agri_image_exchange",
            type=ExchangeType.DIRECT,
            durable=True,
        )

        await self._channel.declare_queue(
            "agri_image_tasks",
            durable=True,
        )

    async def enqueue_image(self, image_url: str) -> None:
        """Publish an image URL for asynchronous processing."""

        if self._exchange is None:
            await self._initialize()

        message = Message(
            image_url.encode(),
            delivery_mode=2,
        )

        await self._exchange.publish(
            message,
            routing_key="agri_image_tasks",
        )

        print(
            f"[ImageProcessingService] Enqueued image URL: {image_url}"
        )