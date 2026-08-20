from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from cshield.scanners import PatternScanner, fingerprint

from .diffs import ChangedLine
from .verdicts import FindingInput


@dataclass(frozen=True)
class DiffFinding:
    fingerprint: str
    rule_id: str
    title: str
    severity: str
    confidence: str
    path: str
    line: int
    evidence: str
    description: str
    remediation: str

    def verdict_input(self) -> FindingInput:
        return FindingInput(self.fingerprint, self.rule_id, self.severity, self.confidence)


def scan_changed_lines(lines: list[ChangedLine]) -> list[DiffFinding]:
    scanner = PatternScanner()
    findings: list[DiffFinding] = []
    for changed in lines:
        suffix = Path(changed.path).suffix.lower()
        for rule in scanner._applicable(suffix):
            if not rule.pattern.search(changed.text):
                continue
            evidence = scanner._redact(changed.text, rule.category)
            finding_fingerprint = fingerprint(rule.id, changed.path, changed.line, evidence)
            findings.append(DiffFinding(
                fingerprint=finding_fingerprint,
                rule_id=rule.id,
                title=rule.title,
                severity=rule.severity.value,
                confidence=rule.confidence.value,
                path=changed.path,
                line=changed.line,
                evidence=evidence,
                description=rule.description,
                remediation=rule.remediation,
            ))
    return findings
