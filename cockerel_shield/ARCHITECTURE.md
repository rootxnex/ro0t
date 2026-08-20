# Architecture

## Current state

The repository contains two divergent copies of a FastAPI/Streamlit prototype. The primary backend accepts a filename, then selects random mock vulnerabilities; it does not inspect source code. The primary frontend is a large single-file dashboard populated mostly by generated demonstration data. JSON files under `data/` act as an append-only scan store.

The first production-oriented slice is the `cshield` package:

```text
CLI -> RepositoryScanner -> ScannerAdapter(s) -> canonical Finding -> deduplication -> JSON/Markdown
```

- `models.py` owns severity, confidence, evidence, and the canonical finding representation.
- `scanners.py` defines the adapter contract and a deliberately small deterministic baseline scanner.
- `engine.py` performs bounded, non-executing repository traversal and deterministic deduplication.
- `reporting.py` renders machine- and human-readable evidence-first reports.
- `__main__.py` provides the local CLI and CI-compatible exit policy.

## Decisions

### Implement the deterministic CLI before dashboard integration

- **Reason:** there was no real scanning engine for the UI or API to expose.
- **Security impact:** repository code is read as hostile data and never executed; symlinks and oversized files are skipped.
- **Alternative considered:** retrofit scanning into the existing `/scan` endpoint.
- **Trade-off:** the dashboard remains a prototype until it can consume stable scan output.

### Use an adapter boundary and a small built-in scanner

- **Reason:** it establishes stable orchestration and finding contracts without making Semgrep installation a prerequisite.
- **Security impact:** built-in rules are deterministic, and secret evidence is redacted in reports.
- **Alternative considered:** directly couple the MVP to Semgrep.
- **Trade-off:** the initial rules are a credible plumbing baseline, not comprehensive SAST. Semgrep, OSV, and a mature secret scanner remain the next adapters.

### Keep severity separate from confidence

- **Reason:** potential impact and evidentiary certainty answer different questions.
- **Security impact:** uncertain pattern matches are not presented as confirmed merely because impact is high.
- **Alternative considered:** one combined risk score.
- **Trade-off:** policy decisions need to consider two fields.
