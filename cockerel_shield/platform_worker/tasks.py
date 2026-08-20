from __future__ import annotations

import os

from celery import Celery

from github_gate.diffs import added_lines
from github_gate.diff_rules import scan_changed_lines
from github_gate.checks import completed_check_payload
from github_gate.verdicts import Disposition, Policy, RulePolicy, evaluate_verdict
from platform_worker.github import GitHubAppClient
from platform_worker.storage import PostgresScanStore

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
    store = PostgresScanStore(_required("DATABASE_URL"))
    scan_id = store.start(
        scan_key=scan_key, delivery_id=delivery_id, repository_id=repository_id,
        pr_number=pull_request_number, head_sha=head_sha,
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
    findings = scan_changed_lines(changed)
    policy = Policy("Balanced", 1, {
        "generic-private-key": RulePolicy(Disposition.BLOCK, "HIGH"),
        "generic-api-token": RulePolicy(Disposition.BLOCK, "HIGH"),
        "python-eval": RulePolicy(Disposition.REVIEW, "HIGH"),
        "javascript-eval": RulePolicy(Disposition.REVIEW, "HIGH"),
        "python-shell-true": RulePolicy(Disposition.REVIEW, "MEDIUM"),
    })
    verdict = evaluate_verdict([item.verdict_input() for item in findings], policy)
    payload = completed_check_payload(
        verdict,
        details_url=f"{_required('PUBLIC_BASE_URL').rstrip('/')}/scans/{scan_id}",
        head_sha=head_sha,
        findings=findings,
    )
    check_run_id = client.create_check_run(
        installation_id=installation_id, repository_id=repository_id, payload=payload,
    )
    store.complete(scan_id=scan_id, result=verdict, findings=findings, check_run_id=check_run_id)
    return {
        "delivery_id": delivery_id,
        "scan_key": scan_key,
        "head_sha": head_sha,
        "files_changed": len(files),
        "added_lines": len(changed),
        "findings": len(findings),
        "verdict": verdict.verdict.value,
        "check_run_id": check_run_id,
        "status": "completed",
    }


def _required(name: str) -> str:
    value = os.environ.get(name, "")
    if not value:
        raise RuntimeError(f"missing required worker configuration: {name}")
    return value
