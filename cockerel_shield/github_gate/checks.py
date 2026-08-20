from __future__ import annotations

from .diff_rules import DiffFinding
from .verdicts import VerdictResult


def completed_check_payload(
    result: VerdictResult, *, details_url: str, head_sha: str,
    findings: list[DiffFinding] | None = None,
) -> dict:
    """Return the stable subset sent to GitHub's Checks API."""
    title = {
        "success": "Safe",
        "neutral": "Review required",
        "failure": "Block",
    }[result.github_conclusion]
    payload = {
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
    annotations = []
    for finding in (findings or [])[:50]:
        level = "failure" if finding.fingerprint in result.blocking_fingerprints else "warning"
        annotations.append({
            "path": finding.path,
            "start_line": finding.line,
            "end_line": finding.line,
            "annotation_level": level,
            "title": finding.title[:255],
            "message": f"{finding.description} Fix: {finding.remediation}"[:65_535],
            "raw_details": finding.evidence[:65_535],
        })
    if annotations:
        payload["output"]["annotations"] = annotations
    return payload
