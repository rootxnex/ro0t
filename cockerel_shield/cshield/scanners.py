from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Protocol

from .models import Confidence, Evidence, Finding, Severity


@dataclass(frozen=True)
class ScanContext:
    scan_id: str
    root: Path


class ScannerAdapter(Protocol):
    name: str

    def scan_file(self, path: Path, relative_path: str, context: ScanContext) -> list[Finding]: ...

    def metadata(self) -> dict[str, str]: ...


@dataclass(frozen=True)
class Rule:
    id: str
    title: str
    pattern: re.Pattern[str]
    category: str
    severity: Severity
    confidence: Confidence
    cwe: tuple[str, ...]
    description: str
    attack_scenario: str
    remediation: str
    extensions: tuple[str, ...] = ()


def fingerprint(rule_id: str, relative_path: str, line: int, normalized: str) -> str:
    material = "\0".join((rule_id, relative_path, str(line), " ".join(normalized.split())))
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


class PatternScanner:
    """Small deterministic baseline scanner; adapters for Semgrep/OSV follow this contract."""

    name = "cshield-patterns"
    version = "0.1.0"

    RULES = (
        Rule(
            "python-eval", "Dynamic code execution with eval", re.compile(r"(?<![\w.])eval\s*\("),
            "CODE_INJECTION", Severity.HIGH, Confidence.HIGH, ("CWE-95",),
            "eval() executes input as Python code and is unsafe when data can be influenced externally.",
            "An attacker who controls the evaluated value may execute arbitrary code in the application process.",
            "Replace eval() with a constrained parser such as json.loads() or ast.literal_eval().",
            (".py",),
        ),
        Rule(
            "python-shell-true", "Subprocess invoked through a shell", re.compile(r"shell\s*=\s*True"),
            "COMMAND_INJECTION", Severity.HIGH, Confidence.MEDIUM, ("CWE-78",),
            "Shell execution expands metacharacters and can turn untrusted input into commands.",
            "If an argument contains attacker-controlled shell syntax, the shell may execute additional commands.",
            "Use subprocess with shell=False and pass an explicit argument list.", (".py",),
        ),
        Rule(
            "javascript-eval", "Dynamic JavaScript execution with eval", re.compile(r"(?<![\w.])eval\s*\("),
            "CODE_INJECTION", Severity.HIGH, Confidence.HIGH, ("CWE-95",),
            "eval() executes a string as JavaScript in the current context.",
            "Attacker-controlled evaluated data can execute script with the application's privileges.",
            "Use JSON.parse() for data or an allow-listed interpreter for expressions.", (".js", ".jsx", ".ts", ".tsx"),
        ),
        Rule(
            "generic-private-key", "Private key committed to repository",
            re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
            "SECRET", Severity.CRITICAL, Confidence.HIGH, ("CWE-798",),
            "A private-key header is present in source-controlled content.",
            "Anyone with repository access may impersonate the key owner or decrypt protected material.",
            "Revoke and rotate the key, remove it from history, and load replacement credentials from a secret store.",
        ),
        Rule(
            "generic-api-token", "Likely hard-coded API credential",
            re.compile(r"(?i)(?:api[_-]?key|secret|token|password)\s*[:=]\s*['\"]([^'\"\s]{16,})['\"]"),
            "SECRET", Severity.HIGH, Confidence.MEDIUM, ("CWE-798",),
            "A credential-like variable is assigned a high-entropy-looking literal.",
            "A repository reader may reuse the credential against its service.",
            "Rotate the credential and reference it through a secret manager or environment variable.",
        ),
    )

    def metadata(self) -> dict[str, str]:
        return {"name": self.name, "version": self.version, "kind": "SAST/SECRETS"}

    def scan_file(self, path: Path, relative_path: str, context: ScanContext) -> list[Finding]:
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            return []
        findings: list[Finding] = []
        for number, line in enumerate(text.splitlines(), 1):
            for rule in self._applicable(path.suffix.lower()):
                match = rule.pattern.search(line)
                if not match:
                    continue
                redacted = self._redact(line, rule.category)
                fp = fingerprint(rule.id, relative_path, number, redacted)
                findings.append(Finding(
                    id=f"CS-{fp[:12]}", scan_id=context.scan_id, scanner=self.name,
                    scanners=[self.name], rule_id=rule.id, title=rule.title,
                    description=rule.description, category=rule.category, severity=rule.severity,
                    confidence=rule.confidence, file=relative_path, start_line=number, end_line=number,
                    evidence=[Evidence(message=f"Rule {rule.id} matched line {number}", snippet=redacted)],
                    attack_scenario=rule.attack_scenario, remediation=rule.remediation,
                    fingerprint=fp, cwe=list(rule.cwe), references=[],
                ))
        return findings

    def _applicable(self, suffix: str) -> Iterable[Rule]:
        return (rule for rule in self.RULES if not rule.extensions or suffix in rule.extensions)

    @staticmethod
    def _redact(line: str, category: str) -> str:
        if category != "SECRET":
            return line.strip()[:300]
        if "PRIVATE KEY" in line:
            return "[REDACTED PRIVATE KEY HEADER]"
        return re.sub(r"(['\"])[^'\"]{8,}\1", r"\1[REDACTED]\1", line.strip())[:300]
