from __future__ import annotations

from dataclasses import dataclass
import re

HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")


@dataclass(frozen=True)
class ChangedLine:
    path: str
    line: int
    text: str


def added_lines(path: str, patch: str, *, max_lines: int = 5_000) -> list[ChangedLine]:
    """Extract added lines with destination line numbers from a unified diff."""
    if not path or path.startswith("/") or "\x00" in path:
        raise ValueError("invalid changed file path")
    result: list[ChangedLine] = []
    new_line: int | None = None
    for raw_line in patch.splitlines():
        match = HUNK.match(raw_line)
        if match:
            new_line = int(match.group(1))
            continue
        if new_line is None or raw_line.startswith("\\ No newline"):
            continue
        if raw_line.startswith("+") and not raw_line.startswith("+++"):
            result.append(ChangedLine(path, new_line, raw_line[1:]))
            if len(result) > max_lines:
                raise ValueError("pull request exceeds the changed-line limit")
            new_line += 1
        elif raw_line.startswith("-") and not raw_line.startswith("---"):
            continue
        else:
            new_line += 1
    return result
