from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Verdict(str, Enum):
    SAFE = "SAFE"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCK = "BLOCK"


class Disposition(str, Enum):
    IGNORE = "IGNORE"
    REVIEW = "REVIEW"
    BLOCK = "BLOCK"


CONFIDENCE_RANK = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}


@dataclass(frozen=True)
class FindingInput:
    fingerprint: str
    rule_id: str
    severity: str
    confidence: str


@dataclass(frozen=True)
class RulePolicy:
    disposition: Disposition
    minimum_confidence: str = "MEDIUM"


@dataclass(frozen=True)
class Policy:
    name: str
    version: int
    rules: dict[str, RulePolicy] = field(default_factory=dict)
    default_disposition: Disposition = Disposition.REVIEW
    default_minimum_confidence: str = "MEDIUM"


@dataclass(frozen=True)
class VerdictResult:
    verdict: Verdict
    blocking_fingerprints: tuple[str, ...]
    review_fingerprints: tuple[str, ...]
    ignored_fingerprints: tuple[str, ...]
    explanation: str

    @property
    def github_conclusion(self) -> str:
        return {
            Verdict.SAFE: "success",
            Verdict.REVIEW_REQUIRED: "neutral",
            Verdict.BLOCK: "failure",
        }[self.verdict]


def evaluate_verdict(
    findings: list[FindingInput], policy: Policy, *, excepted_fingerprints: set[str] | None = None
) -> VerdictResult:
    exceptions = excepted_fingerprints or set()
    blocking: list[str] = []
    review: list[str] = []
    ignored: list[str] = []
    for finding in findings:
        if finding.fingerprint in exceptions:
            ignored.append(finding.fingerprint)
            continue
        rule = policy.rules.get(finding.rule_id)
        disposition = rule.disposition if rule else policy.default_disposition
        minimum = rule.minimum_confidence if rule else policy.default_minimum_confidence
        if CONFIDENCE_RANK.get(finding.confidence, 0) < CONFIDENCE_RANK.get(minimum, 2):
            ignored.append(finding.fingerprint)
        elif disposition is Disposition.BLOCK:
            blocking.append(finding.fingerprint)
        elif disposition is Disposition.REVIEW:
            review.append(finding.fingerprint)
        else:
            ignored.append(finding.fingerprint)

    if blocking:
        verdict = Verdict.BLOCK
        explanation = f"{len(blocking)} finding(s) are prohibited by {policy.name} v{policy.version}."
    elif review:
        verdict = Verdict.REVIEW_REQUIRED
        explanation = f"{len(review)} finding(s) require human review under {policy.name} v{policy.version}."
    else:
        verdict = Verdict.SAFE
        explanation = f"No active finding exceeds the threshold in {policy.name} v{policy.version}."
    return VerdictResult(verdict, tuple(blocking), tuple(review), tuple(ignored), explanation)
