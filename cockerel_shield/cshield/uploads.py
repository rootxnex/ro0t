from __future__ import annotations

import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePath
from typing import Iterable

from .engine import RepositoryScanner, ScanResult

MAX_FILE_BYTES = 1_000_000
MAX_TOTAL_BYTES = 10_000_000
MAX_FILES = 100


class UploadError(ValueError):
    pass


@dataclass(frozen=True)
class UploadedSource:
    name: str
    content: bytes


def scan_uploads(files: Iterable[UploadedSource]) -> ScanResult:
    uploads = list(files)
    if not uploads:
        raise UploadError("select at least one source file")
    if len(uploads) > MAX_FILES:
        raise UploadError(f"a scan is limited to {MAX_FILES} files")
    if sum(len(item.content) for item in uploads) > MAX_TOTAL_BYTES:
        raise UploadError("uploaded files exceed the 10 MB scan limit")

    with tempfile.TemporaryDirectory(prefix="cshield-upload-") as directory:
        root = Path(directory)
        names: set[str] = set()
        for item in uploads:
            name = _safe_name(item.name)
            if name in names:
                raise UploadError(f"duplicate filename: {name}")
            if len(item.content) > MAX_FILE_BYTES:
                raise UploadError(f"{name} exceeds the 1 MB per-file limit")
            names.add(name)
            (root / name).write_bytes(item.content)
        return RepositoryScanner(max_file_bytes=MAX_FILE_BYTES).scan(root)


def _safe_name(value: str) -> str:
    # Uploaded files are intentionally flattened. Archive and directory upload support
    # needs a separate, traversal-safe manifest format.
    if not value or "\x00" in value or PurePath(value).name != value or value in {".", ".."}:
        raise UploadError("filenames must not contain paths")
    return value
