from __future__ import annotations

import json

from .engine import ScanResult


def json_report(result: ScanResult) -> str:
    return json.dumps(result.to_dict(), indent=2) + "\n"


def markdown_report(result: ScanResult) -> str:
    lines = ["# Cockerel Shield security report", "", f"- Scan ID: `{result.scan_id}`",
             f"- Target: `{result.target}`", f"- Files scanned: {result.files_scanned}",
             f"- Findings: {len(result.findings)}", ""]
    if not result.findings:
        lines.append("No findings were produced by the configured scanners.")
    for finding in result.findings:
        lines += [f"## {finding.severity.value}: {finding.title}", "",
                  f"`{finding.file}:{finding.start_line}` · Confidence: **{finding.confidence.value}** · {', '.join(finding.cwe)}",
                  "", finding.description, "", "**Evidence**", "", f"```text\n{finding.evidence[0].snippet}\n```",
                  "", "**Defensive attack scenario**", "", finding.attack_scenario,
                  "", "**Remediation**", "", finding.remediation, ""]
    return "\n".join(lines) + "\n"
