from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .engine import RepositoryScanner, ScanError
from .models import Severity
from .reporting import json_report, markdown_report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="cshield", description="Evidence-first repository security scanner")
    parser.add_argument("command", choices=["scan"])
    parser.add_argument("target", nargs="?", default=".")
    parser.add_argument("--format", choices=["json", "markdown"], default="markdown")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--fail-on", choices=["critical", "high", "medium", "low", "never"], default="never")
    args = parser.parse_args(argv)
    try:
        result = RepositoryScanner().scan(Path(args.target))
    except ScanError as error:
        print(f"cshield: {error}", file=sys.stderr)
        return 2
    rendered = json_report(result) if args.format == "json" else markdown_report(result)
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    if args.fail_on == "never":
        return 0
    order = {Severity.INFO: 0, Severity.LOW: 1, Severity.MEDIUM: 2, Severity.HIGH: 3, Severity.CRITICAL: 4}
    threshold = order[Severity(args.fail_on.upper())]
    return 1 if any(order[finding.severity] >= threshold for finding in result.findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
