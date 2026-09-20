"""In-memory store for uploaded images between segment -> classify calls.

Bounded (FIFO eviction) so long-running containers don't leak memory.
"""

import uuid
from collections import OrderedDict

from app.config import settings


class ImageStore:
    def __init__(self, max_items: int = settings.STORE_MAX_ITEMS):
        self._items: OrderedDict[str, dict] = OrderedDict()
        self.max_items = max_items

    def save(self, image, leaves: list) -> str:
        image_id = uuid.uuid4().hex
        self._items[image_id] = {"image": image, "leaves": leaves}
        self._items.move_to_end(image_id)
        while len(self._items) > self.max_items:
            self._items.popitem(last=False)
        return image_id

    def get(self, image_id: str) -> dict | None:
        return self._items.get(image_id)

    def update_leaves(self, image_id: str, leaves: list) -> None:
        self._items[image_id]["leaves"] = leaves


store = ImageStore()
