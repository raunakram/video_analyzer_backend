from typing import List, Optional

from app.models.item import Item
from app.schemas.item import ItemCreate


class ItemService:
    """Simple in-memory service for Items. Replace with DB-backed service as needed."""

    def __init__(self):
        self._items: List[Item] = []
        self._next_id = 1

    def create(self, payload: ItemCreate) -> Item:
        item = Item(id=self._next_id, name=payload.name, description=payload.description)
        self._items.append(item)
        self._next_id += 1
        return item

    def list_all(self) -> List[Item]:
        return list(self._items)

    def get(self, item_id: int) -> Optional[Item]:
        return next((i for i in self._items if i.id == item_id), None)
