from __future__ import annotations

from functools import lru_cache

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from github_gate.service import GitHubWebhookService
from github_gate.webhooks import MAX_WEBHOOK_BYTES, WebhookError
from platform_api.adapters import CeleryScanQueue, PostgresDeliveryStore
from platform_api.settings import Settings

app = FastAPI(title="Cocokerel Platform API", version="0.1.0", docs_url=None, redoc_url=None)


@lru_cache(maxsize=1)
def webhook_service() -> GitHubWebhookService:
    settings = Settings.from_environment()
    return GitHubWebhookService(
        secret=settings.github_webhook_secret,
        deliveries=PostgresDeliveryStore(settings.database_url),
        queue=CeleryScanQueue(settings.redis_url),
    )


@app.get("/healthz")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/webhooks/github")
async def github_webhook(request: Request) -> JSONResponse:
    try:
        declared_length = int(request.headers.get("content-length", "0") or 0)
    except ValueError:
        return JSONResponse({"error": "invalid_content_length"}, status_code=400)
    if declared_length > MAX_WEBHOOK_BYTES:
        return JSONResponse({"error": "payload_too_large"}, status_code=413)
    body = await request.body()
    try:
        result = webhook_service().accept(request.headers, body)
    except WebhookError as error:
        return JSONResponse({"error": str(error)}, status_code=400)
    except Exception:
        # Do not leak database, queue, or credential details to webhook callers.
        return JSONResponse({"error": "temporary_processing_failure"}, status_code=503)
    return JSONResponse({
        "accepted": True,
        "delivery_id": result.delivery_id,
        "duplicate": result.duplicate,
        "scan_queued": result.scan_queued,
        "job_id": result.job_id,
    })
