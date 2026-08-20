from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class Confidence(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass(frozen=True)
class Evidence:
    message: str
    snippet: str
    kind: str = "code"


@dataclass
class Finding:
    id: str
    scan_id: str
    scanner: str
    rule_id: str
    title: str
    description: str
    category: str
    severity: Severity
    confidence: Confidence
    file: str
    start_line: int
    end_line: int
    evidence: list[Evidence]
    attack_scenario: str
    remediation: str
    fingerprint: str
    cwe: list[str] = field(default_factory=list)
    cve: list[str] = field(default_factory=list)
    references: list[str] = field(default_factory=list)
    scanners: list[str] = field(default_factory=list)
    status: str = "OPEN"

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["severity"] = self.severity.value
        result["confidence"] = self.confidence.value
        return result
