from __future__ import annotations

import os
import time
import uuid
from dataclasses import dataclass
from pathlib import Path

from .models import Finding
from .scanners import PatternScanner, ScanContext, ScannerAdapter

IGNORED_DIRS = {".git", ".hg", ".svn", "node_modules", "vendor", ".venv", "venv", "dist", "build", "__pycache__"}


@dataclass(frozen=True)
class ScanResult:
    scan_id: str
    target: str
    started_at: str
    duration_ms: int
    files_scanned: int
    files_skipped: int
    findings: list[Finding]
    scanners: list[dict[str, str]]

    def to_dict(self) -> dict[str, object]:
        return {
            "schemaVersion": "1.0", "scanId": self.scan_id, "target": self.target,
            "startedAt": self.started_at, "durationMs": self.duration_ms,
            "filesScanned": self.files_scanned, "filesSkipped": self.files_skipped,
            "scanners": self.scanners, "findings": [finding.to_dict() for finding in self.findings],
        }


class ScanError(ValueError):
    pass


class RepositoryScanner:
    def __init__(self, adapters: list[ScannerAdapter] | None = None, max_file_bytes: int = 1_000_000) -> None:
        self.adapters = adapters or [PatternScanner()]
        self.max_file_bytes = max_file_bytes

    def scan(self, target: Path) -> ScanResult:
        root = target.resolve()
        if not root.exists() or not root.is_dir():
            raise ScanError(f"target is not a directory: {target}")
        scan_id = str(uuid.uuid4())
        started = time.time()
        started_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(started))
        context = ScanContext(scan_id=scan_id, root=root)
        findings: list[Finding] = []
        scanned = skipped = 0
        for path in self._files(root):
            try:
                stat = path.lstat()
                if path.is_symlink() or not path.is_file() or stat.st_size > self.max_file_bytes:
                    skipped += 1
                    continue
                relative = path.relative_to(root).as_posix()
            except (OSError, ValueError):
                skipped += 1
                continue
            scanned += 1
            for adapter in self.adapters:
                findings.extend(adapter.scan_file(path, relative, context))
        unique = self._deduplicate(findings)
        duration = int((time.time() - started) * 1000)
        return ScanResult(scan_id, str(root), started_at, duration, scanned, skipped, unique,
                          [adapter.metadata() for adapter in self.adapters])

    @staticmethod
    def _files(root: Path):
        for current, dirs, files in os.walk(root, topdown=True, followlinks=False):
            dirs[:] = sorted(d for d in dirs if d not in IGNORED_DIRS and not (Path(current) / d).is_symlink())
            for name in sorted(files):
                yield Path(current) / name

    @staticmethod
    def _deduplicate(findings: list[Finding]) -> list[Finding]:
        unique: dict[str, Finding] = {}
        for finding in findings:
            existing = unique.get(finding.fingerprint)
            if existing is None:
                unique[finding.fingerprint] = finding
                continue
            existing.scanners = sorted(set(existing.scanners + finding.scanners))
            existing.evidence.extend(item for item in finding.evidence if item not in existing.evidence)
        return sorted(unique.values(), key=lambda item: (item.file, item.start_line, item.rule_id))
