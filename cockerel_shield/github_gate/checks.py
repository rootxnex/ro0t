from __future__ import annotations

from .verdicts import VerdictResult


def completed_check_payload(result: VerdictResult, *, details_url: str, head_sha: str) -> dict:
    """Return the stable subset sent to GitHub's Checks API."""
    title = {
        "success": "Safe",
        "neutral": "Review required",
        "failure": "Block",
    }[result.github_conclusion]
    return {
        "name": "Cocokerel Security Verdict",
        "head_sha": head_sha,
        "status": "completed",
        "conclusion": result.github_conclusion,
        "details_url": details_url,
        "output": {
            "title": title,
            "summary": result.explanation,
        },
    }
