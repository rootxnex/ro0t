from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Protocol

from .delivery import DeliveryStore
from .webhooks import GitHubWebhook, parse_github_webhook


class ScanQueue(Protocol):
    def enqueue(self, event: GitHubWebhook) -> str: ...


@dataclass(frozen=True)
class WebhookAcceptance:
    delivery_id: str
    duplicate: bool
    scan_queued: bool
    job_id: str | None


class GitHubWebhookService:
    def __init__(self, *, secret: str, deliveries: DeliveryStore, queue: ScanQueue):
        self._secret = secret
        self._deliveries = deliveries
        self._queue = queue

    def accept(self, headers: Mapping[str, str], body: bytes) -> WebhookAcceptance:
        event = parse_github_webhook(secret=self._secret, headers=headers, body=body)
        if not self._deliveries.accept_once(event.delivery_id):
            return WebhookAcceptance(event.delivery_id, True, False, None)
        job_id = self._queue.enqueue(event) if event.should_scan else None
        return WebhookAcceptance(event.delivery_id, False, job_id is not None, job_id)
