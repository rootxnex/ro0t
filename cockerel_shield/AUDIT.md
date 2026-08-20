# Repository audit and MVP backlog

## Structure, features, and architecture

The project is a Python prototype: FastAPI backend, Streamlit frontend, JSON scan history, shell launcher, and a live-service smoke test. A second nested `cockerel_shield/cockerel_shield` copy has older and divergent versions of the same app. The advertised dashboard, network map, threat detection, vulnerability scanner, and bounty views are primarily simulated. The backend has health, mock scan, and history endpoints.

## Security weaknesses and incomplete behavior

1. `/scan` does not receive or inspect code; it randomly assigns fictional findings and CVEs from a filename extension.
2. API exceptions expose raw exception strings, while scan history returns an unbounded shared JSON document.
3. JSON persistence has no locking, atomic writes, schema migration, authorization, or corruption recovery.
4. The dashboard advertises target/network scanning and automated response without implementing them; this creates unsafe expectations.
5. Uploaded file UI metadata is displayed, but content does not reach a deterministic scanning engine.
6. There are no unit, security, normalization, traversal, or report tests; the only test needs running services.
7. Dependencies are old exact pins without hashes or automated vulnerability review. `uvicorn[standard]` also allows transitive variation.
8. `start.sh` uses development reload while listening on all interfaces. Logs, bytecode, and generated scan data are committed.
9. The root security policy is an unedited template with fictitious supported versions.
10. There is no authentication, rate limiting, CSRF model, audit log, data retention policy, or isolation boundary.

## Remove or postpone

Remove the random claims and mock CVEs from any product-facing release. Postpone network scanning, automated response, predictive AI, bug-bounty payouts, scheduling, multi-tenancy, and enterprise features until repository scanning is trustworthy. Keep the existing dashboard clearly labeled as prototype data until it is replaced.

## Recommended MVP architecture

Use a modular monolith: local CLI and later FastAPI call the same scan application service; adapters integrate Semgrep, OSV, and a mature secret scanner; all outputs normalize into a canonical finding; deterministic deduplication precedes SQLite persistence and report rendering. AI remains optional and downstream of evidence, with explicit data-sharing configuration.

## Prioritized backlog

1. **Completed in this milestone:** deterministic local scan, canonical findings, evidence, redaction, deduplication, safe traversal, reports, and CI exit codes.
2. Add sandboxed Semgrep adapter with pinned rules, timeouts, output-size limits, and malformed-output tests.
3. Add OSV lockfile adapter and a mature secret-scanning adapter; preserve raw evidence securely.
4. Replace random API behavior with the shared scan service and SQLite scan history.
5. Replace simulated dashboard pages with project, scan, and finding views backed by the API.
6. Add Git repository acquisition with strict scheme/host, size, ref, timeout, and credential controls.
7. Add CI workflow, dependency auditing, packaging, and release artifacts.
8. Add opt-in AI provider abstraction only after privacy/redaction controls exist.

## Highest-value next feature

The implemented milestone is the deterministic local repository scan pipeline. The next highest-value feature after this change is a hardened Semgrep adapter, because it expands detection coverage while preserving the stable evidence and reporting contracts established here.
