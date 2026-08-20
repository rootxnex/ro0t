from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass
from typing import Any, Mapping

MAX_WEBHOOK_BYTES = 1_000_000
PR_SCAN_ACTIONS = frozenset({"opened", "reopened", "synchronize", "ready_for_review"})
SUPPORTED_EVENTS = frozenset({"installation", "installation_repositories", "pull_request"})


class WebhookError(ValueError):
    """A GitHub webhook is invalid or outside the accepted contract."""


@dataclass(frozen=True)
class GitHubWebhook:
    delivery_id: str
    event: str
    action: str
    payload: Mapping[str, Any]
    should_scan: bool
    repository_id: int | None
    pull_request_number: int | None
    head_sha: str | None
    installation_id: int | None

    @property
    def scan_key(self) -> str | None:
        if not self.should_scan:
            return None
        return f"github:{self.repository_id}:pr:{self.pull_request_number}:sha:{self.head_sha}"


def sign_payload(secret: str, body: bytes) -> str:
    digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


def verify_signature(secret: str, body: bytes, signature: str | None) -> None:
    if not secret:
        raise WebhookError("webhook secret is not configured")
    if not signature or not signature.startswith("sha256="):
        raise WebhookError("missing or malformed webhook signature")
    if not hmac.compare_digest(sign_payload(secret, body), signature):
        raise WebhookError("invalid webhook signature")


def parse_github_webhook(
    *, secret: str, headers: Mapping[str, str], body: bytes
) -> GitHubWebhook:
    if len(body) > MAX_WEBHOOK_BYTES:
        raise WebhookError("webhook body exceeds the 1 MB limit")
    lowered = {key.lower(): value for key, value in headers.items()}
    if "application/json" not in lowered.get("content-type", ""):
        raise WebhookError("webhook content type must be application/json")
    delivery_id = lowered.get("x-github-delivery", "").strip()
    event = lowered.get("x-github-event", "").strip()
    if not delivery_id or len(delivery_id) > 100:
        raise WebhookError("missing or invalid GitHub delivery ID")
    if event not in SUPPORTED_EVENTS:
        raise WebhookError("unsupported GitHub event")
    verify_signature(secret, body, lowered.get("x-hub-signature-256"))
    try:
        payload = json.loads(body)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise WebhookError("webhook body is not valid JSON") from error
    if not isinstance(payload, dict):
        raise WebhookError("webhook body must be a JSON object")

    action = str(payload.get("action", ""))
    repository = payload.get("repository") or {}
    pull_request = payload.get("pull_request") or {}
    repository_id = _positive_int(repository.get("id"))
    pr_number = _positive_int(payload.get("number"))
    head_sha = str((pull_request.get("head") or {}).get("sha", "")) or None
    installation_id = _positive_int((payload.get("installation") or {}).get("id"))
    is_draft = bool(pull_request.get("draft", False))
    should_scan = (
        event == "pull_request"
        and action in PR_SCAN_ACTIONS
        and repository_id is not None
        and pr_number is not None
        and _valid_sha(head_sha)
        and installation_id is not None
        and (not is_draft or action == "ready_for_review")
    )
    return GitHubWebhook(
        delivery_id=delivery_id,
        event=event,
        action=action,
        payload=payload,
        should_scan=should_scan,
        repository_id=repository_id,
        pull_request_number=pr_number,
        head_sha=head_sha,
        installation_id=installation_id,
    )


def _positive_int(value: object) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) and value > 0 else None


def _valid_sha(value: str | None) -> bool:
    if not value or len(value) != 40:
        return False
    return all(character in "0123456789abcdefABCDEF" for character in value)
