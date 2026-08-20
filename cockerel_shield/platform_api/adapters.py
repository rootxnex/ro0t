from __future__ import annotations

from celery import Celery
from psycopg import connect

from github_gate.webhooks import GitHubWebhook


class PostgresDeliveryStore:
    def __init__(self, database_url: str):
        self._database_url = database_url

    def accept_once(self, delivery_id: str) -> bool:
        with connect(self._database_url) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO webhook_deliveries (delivery_id, status)
                    VALUES (%s, 'accepted')
                    ON CONFLICT (delivery_id) DO NOTHING
                    RETURNING delivery_id
                    """,
                    (delivery_id,),
                )
                return cursor.fetchone() is not None


class CeleryScanQueue:
    def __init__(self, redis_url: str):
        self._celery = Celery("cocokerel-api", broker=redis_url, backend=redis_url)

    def enqueue(self, event: GitHubWebhook) -> str:
        result = self._celery.send_task(
            "platform_worker.scan_pull_request",
            kwargs={
                "delivery_id": event.delivery_id,
                "repository_id": event.repository_id,
                "pull_request_number": event.pull_request_number,
                "head_sha": event.head_sha,
                "scan_key": event.scan_key,
            },
            task_id=event.scan_key,
        )
        return str(result.id)
