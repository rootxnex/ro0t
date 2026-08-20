from __future__ import annotations

from dataclasses import dataclass, field
from threading import Lock
from typing import Protocol


class DeliveryStore(Protocol):
    def accept_once(self, delivery_id: str) -> bool: ...


@dataclass
class MemoryDeliveryStore:
    """Thread-safe development adapter; production uses a unique PostgreSQL key."""

    _delivery_ids: set[str] = field(default_factory=set)
    _lock: Lock = field(default_factory=Lock)

    def accept_once(self, delivery_id: str) -> bool:
        with self._lock:
            if delivery_id in self._delivery_ids:
                return False
            self._delivery_ids.add(delivery_id)
            return True
