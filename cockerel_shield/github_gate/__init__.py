"""Core domain logic for the Cocokerel GitHub pull-request security gate."""

from .verdicts import FindingInput, Policy, RulePolicy, Verdict, evaluate_verdict
from .webhooks import WebhookError, parse_github_webhook

__all__ = [
    "FindingInput",
    "Policy",
    "RulePolicy",
    "Verdict",
    "WebhookError",
    "evaluate_verdict",
    "parse_github_webhook",
]
