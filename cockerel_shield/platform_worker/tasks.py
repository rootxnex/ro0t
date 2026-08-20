from __future__ import annotations

import os

from celery import Celery

from github_gate.diffs import added_lines
from platform_worker.github import GitHubAppClient

celery_app = Celery("cocokerel-worker", broker=os.environ.get("REDIS_URL"), backend=os.environ.get("REDIS_URL"))


@celery_app.task(name="platform_worker.scan_pull_request", bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def scan_pull_request(
    self,
    *,
    delivery_id: str,
    repository_id: int,
    pull_request_number: int,
    head_sha: str,
    scan_key: str,
    installation_id: int,
) -> dict:
    client = GitHubAppClient(
        app_id=_required("GITHUB_APP_ID"),
        private_key=_required("GITHUB_APP_PRIVATE_KEY").replace("\\n", "\n"),
    )
    files = client.pull_request_files(
        installation_id=installation_id,
        repository_id=repository_id,
        number=pull_request_number,
    )
    changed = []
    for item in files:
        patch = item.get("patch")
        filename = item.get("filename")
        if isinstance(patch, str) and isinstance(filename, str):
            changed.extend(added_lines(filename, patch))
    return {
        "delivery_id": delivery_id,
        "scan_key": scan_key,
        "head_sha": head_sha,
        "files_changed": len(files),
        "added_lines": len(changed),
        "status": "fetched",
    }


def _required(name: str) -> str:
    value = os.environ.get(name, "")
    if not value:
        raise RuntimeError(f"missing required worker configuration: {name}")
    return value
