# Cocokerel Shield — GitHub PR Security Gate MVP

**Status:** Draft for implementation  
**Product promise:** Every new pull request receives a fast, evidence-based security verdict before merge.

## 1. Purpose

Cocokerel Shield is a security review gate for AI-assisted and rapidly generated code. The MVP integrates with GitHub, scans pull-request changes, explains high-signal risks with file and line evidence, and publishes a transparent merge verdict.

The MVP must prove that development teams keep Cocokerel installed, trust its findings, and use its verdicts during normal pull-request review.

## 2. Goals and exclusions

### Goals

- Complete installation and first scan without manual file upload.
- Scan changed lines plus bounded surrounding context on every relevant PR update.
- Publish a GitHub Check with a `Safe`, `Review required`, or `Block` verdict.
- Provide evidence, remediation, and approved-rule metadata for every finding.
- Offer suggested patches only for deterministic, high-confidence fixes.
- Retain repository scan history, decisions, policy exceptions, and downloadable reports.
- Finish typical scans quickly enough to remain in the pull-request feedback loop.

### Not in MVP

- Billing, subscriptions, or usage metering.
- GitLab, Bitbucket, IDE, or coding-agent integrations.
- AI-authorship detection or scoring.
- Autonomous patch application or merging.
- Enterprise compliance frameworks and custom report builders.
- Full-repository scans on every PR.
- Runtime penetration testing or executing repository code.

## 3. Primary users

- **Developer:** needs a clear finding, exact evidence, and a safe remediation before merging.
- **Repository administrator:** installs the GitHub App, selects repositories, and sets the default policy.
- **Security reviewer:** reviews exceptions, dismissals, trends, and audit history.

## 4. Core workflow

```text
Install GitHub App
  → select repositories and policy
  → PR opened or updated
  → webhook verified and stored
  → scan job queued
  → changed code and context fetched
  → deterministic checks run
  → verdict calculated
  → GitHub Check completed
  → findings and patches reviewed in Cocokerel
```

### Installation flow

1. User signs in to Cocokerel with GitHub.
2. User chooses **Install GitHub App**.
3. GitHub handles organization and repository selection.
4. GitHub redirects to the Cocokerel setup callback with an installation ID.
5. Cocokerel validates access, imports selected repository metadata, and asks for a default policy.
6. Cocokerel confirms the installation and waits for PR events.
7. If an eligible open PR exists, the user may trigger one first scan; otherwise the first scan begins on the next PR event.

Required GitHub App access should be minimal:

- Metadata: read
- Contents: read
- Pull requests: read
- Checks: read and write

Subscribe to installation, installation repositories, pull request, and pull request review events. Request no source-code write permission in the MVP.

## 5. Screens

### Marketing and sign-in

- Headline: **Ship AI-generated code without shipping its vulnerabilities.**
- GitHub sign-in and GitHub App installation calls to action.
- Link to the existing upload/public-repository demo.

### Setup

- Installation and selected-repository status.
- Default policy selector: `Balanced` initially; `Observe` and `Strict` optional.
- Required-permissions explanation and connection errors.

### Repository list

- Repository name, installation, latest verdict, open PR count, last scan, and policy.
- Empty, disconnected, suspended, and failed states.

### Repository detail

- Active PR scans, recent verdict history, policy, finding trend, and installation health.

### Pull-request scan detail

- PR identity, commit SHA, scan status, duration, verdict, and policy version.
- Findings ordered by verdict impact, severity, confidence, and file.
- Each finding shows rule ID/version, file and line, redacted evidence, plain-language risk, remediation, and status.
- Suggested patch shown as an exact unified diff with **Copy patch** or **Download patch**. No automatic application.
- Actions: acknowledge, dismiss with reason, create time-bounded policy exception, and rescan.

### History and report

- Filterable scan history by repository, verdict, rule, and date.
- Immutable JSON and Markdown report downloads for completed scans.
- Audit events for policy and finding decisions.

## 6. Webhook and job lifecycle

### Accepted events

- `installation.created`, `installation.deleted`, `installation.suspend`, `installation.unsuspend`
- `installation_repositories.added`, `installation_repositories.removed`
- `pull_request.opened`, `pull_request.reopened`, `pull_request.synchronize`, `pull_request.ready_for_review`
- Optional rescan after `pull_request_review.submitted` only when an active policy exception requires approval.

Draft PRs are recorded but not scanned until marked ready, unless the repository policy explicitly enables draft scanning.

### Processing requirements

1. Verify `X-Hub-Signature-256` against the raw request body before parsing.
2. Enforce body-size and content-type limits.
3. Deduplicate using `X-GitHub-Delivery`; return success for an already accepted delivery.
4. Store event metadata and enqueue work; respond to GitHub within 10 seconds.
5. Create an in-progress GitHub Check for the PR head SHA.
6. Obtain a short-lived GitHub installation token; never persist it.
7. Fetch PR files, patch data, changed blobs, manifests, and only the bounded context required by enabled rules.
8. Abort superseded scans when a newer head SHA arrives.
9. Run versioned scanners, normalize findings, calculate the verdict, persist the result, and generate reports.
10. Complete the GitHub Check with a summary and deep links.

### Scan states

`queued → fetching → scanning → evaluating → reporting → completed`

Terminal alternatives: `failed`, `cancelled`, and `superseded`. Jobs must be idempotent by repository, PR number, head SHA, and policy version.

## 7. Verdict model

Verdicts are deterministic outputs of the policy version stored on the scan.

| Verdict | Meaning | GitHub Check conclusion |
|---|---|---|
| Safe | No active finding exceeds the configured threshold. | `success` |
| Review required | At least one active finding requires human judgment, but none meets a blocking rule. | `neutral` |
| Block | At least one active, high-confidence finding is prohibited by policy. | `failure` |

Evaluation order:

1. Remove findings covered by an active, scoped policy exception.
2. Apply rule overrides and minimum confidence requirements.
3. `Block` if any remaining finding matches a blocking rule.
4. Otherwise return `Review required` if any remaining finding matches a review rule.
5. Otherwise return `Safe`.

The GitHub Check must state which findings determined the verdict. An operational scan failure must return `action_required`, never `Safe`.

Suggested patches are allowed only when a rule has a deterministic transformation, confidence is high, the patch changes only PR-owned lines, and applying it does not require secret or business-logic inference.

## 8. Initial rule families

Target 15–25 high-signal rules across:

- Committed credentials and private keys
- Shell/command injection and dangerous subprocess use
- Dynamic code execution
- Authentication or authorization bypass patterns
- Unsafe deserialization
- SSRF-prone outbound requests
- Path traversal and dangerous file uploads
- Unverified webhook signatures
- Overly broad CORS, IAM, and infrastructure permissions
- Public database, storage, firewall, and debug/admin configuration
- Insecure cryptography defaults
- Suspicious, nonexistent, or confusion-prone dependencies
- Unsafe AI-agent tool permissions and prompt-to-tool paths
- Missing validation or rate limiting at sensitive boundaries

Each rule must define an ID, version, category, severity, confidence, supported languages, evidence strategy, remediation, references, policy default, test fixtures, and optional deterministic patch generator.

## 9. Data model

All primary keys are UUIDs. Store timestamps in UTC and use soft deletion where GitHub resources may later be restored.

- **organizations:** name, GitHub organization ID, plan placeholder, created_at
- **users:** GitHub user ID, login, display name, email if granted, created_at
- **organization_members:** organization_id, user_id, role
- **github_installations:** organization_id, GitHub installation ID, account ID/type, status, permissions, repository_selection
- **repositories:** installation_id, GitHub repository ID, owner, name, default_branch, visibility, status, policy_id
- **pull_requests:** repository_id, GitHub PR ID/number, title, author, base SHA, head SHA, state, draft, URL
- **scans:** pull_request_id, head SHA, policy_version_id, status, verdict, timestamps, duration, error code, files/lines scanned, report keys
- **findings:** scan_id, fingerprint, rule ID/version, category, severity, confidence, file, start/end line, redacted evidence, description, remediation, status, verdict impact
- **suggested_patches:** finding_id, base blob SHA, unified diff, generator version, validation status
- **policies:** organization_id, name, description, active version
- **policy_versions:** policy_id, immutable rule configuration, thresholds, created_by, created_at
- **policy_exceptions:** organization/repository/rule/fingerprint scope, reason, approver, starts_at, expires_at, status
- **finding_decisions:** finding fingerprint, repository_id, decision, reason, actor, created_at
- **webhook_deliveries:** GitHub delivery ID, event, action, signature_valid, payload reference/hash, received_at, processed_at, status
- **audit_events:** organization_id, actor, action, resource type/ID, metadata, timestamp

Do not store GitHub installation access tokens. Encrypt OAuth refresh tokens and report objects with managed keys. Redact secret evidence before database or object-storage writes.

## 10. API surface

### Authentication and setup

- `GET /api/auth/github/start`
- `GET /api/auth/github/callback`
- `GET /api/github/install`
- `GET /api/github/setup`
- `POST /api/github/setup`
- `POST /api/webhooks/github`

### Dashboard

- `GET /api/repositories`
- `GET /api/repositories/{repository_id}`
- `PATCH /api/repositories/{repository_id}/policy`
- `GET /api/repositories/{repository_id}/pull-requests`
- `GET /api/pull-requests/{pull_request_id}/scans`
- `GET /api/scans/{scan_id}`
- `POST /api/scans/{scan_id}/retry`
- `GET /api/scans/{scan_id}/report.{json|md}`
- `POST /api/findings/{finding_id}/decisions`
- `POST /api/policy-exceptions`
- `DELETE /api/policy-exceptions/{exception_id}`

Every organization-scoped endpoint must enforce membership and role authorization. Mutation requests require CSRF protection where cookie authentication is used.

## 11. Architecture and security boundaries

- **Web:** Next.js dashboard and API gateway, or Next.js plus a private FastAPI service.
- **Database:** PostgreSQL with organization-scoped access patterns.
- **Queue:** Redis with BullMQ for a TypeScript worker, or Celery for a Python worker. Choose one job ecosystem for the MVP.
- **Worker:** isolated scanner process with CPU, memory, file-count, byte, and time limits.
- **Reports:** private object storage using short-lived signed download URLs.
- **GitHub:** App private key stored only in a managed secret store; installation tokens minted per job.

Repository files are hostile data. Never execute builds, package lifecycle scripts, macros, or repository binaries. Block symlinks and archive traversal. Restrict worker egress to GitHub and explicitly approved dependency advisory services. Log identifiers and outcomes, not source code or secrets.

## 12. GitHub Check presentation

The check title is **Cocokerel Security Verdict**. Its summary contains:

- Verdict and one-sentence explanation
- Counts by blocking/review severity
- Scan duration, commit SHA, and policy name/version
- Up to the highest-priority annotations within GitHub limits
- Link to the full Cocokerel scan

Re-running a scan creates or updates the check run for the same head SHA without duplicating findings.

## 13. Service targets

- Webhook acknowledgement: p95 under 2 seconds; hard limit 10 seconds.
- Typical PR scan (≤20 changed files, ≤2,000 changed lines): median under 30 seconds, p95 under 90 seconds.
- GitHub Check published for at least 99% of accepted, eligible PR events.
- No source or secret value appears in application logs.
- Reports remain reproducible from the stored rule and policy versions.

## 14. MVP acceptance criteria

The MVP is complete when all conditions below pass in a production-like environment:

1. A GitHub organization owner can install the App on selected repositories and choose a default policy.
2. Opening or updating a ready PR creates exactly one scan for its current head SHA.
3. Invalid webhook signatures are rejected; duplicate deliveries do not duplicate jobs or scans.
4. The worker scans only changed files/lines plus documented bounded context and never executes repository content.
5. A seeded safe PR produces a successful `Safe` Check.
6. A seeded review-level PR produces a neutral `Review required` Check with file/line evidence.
7. A seeded prohibited, high-confidence issue produces a failed `Block` Check.
8. Every verdict-determining finding links to a view containing evidence, explanation, remediation, rule version, and policy impact.
9. Eligible high-confidence findings can display an exact suggested diff; uncertain findings cannot.
10. A newer PR commit supersedes any older active scan and reports only against the new head SHA.
11. Authorized users can dismiss a finding or create an expiring exception, with an audit event and recalculated verdict.
12. Completed scans remain visible in repository history and export valid JSON and Markdown reports.
13. Installation suspension/deletion prevents new GitHub access and scans.
14. Cross-organization access tests, SSRF tests, archive traversal tests, secret-redaction tests, and job-limit tests pass.
15. Operational failures never result in a `Safe` verdict.

## 15. Launch metrics

- Installation-to-first-scan completion rate
- Median and p95 scan duration
- Weekly repositories with at least one PR scan
- Findings accepted, dismissed, and excepted by rule
- False-positive rate per rule
- Suggested patches viewed, copied/downloaded, and reported as applied
- Repositories enabling blocking policies
- App retention at 7, 30, and 90 days

## 16. Delivery sequence

1. GitHub App registration, installation callback, webhook verification, and repository sync.
2. PR/head-SHA persistence, idempotent job queue, and in-progress GitHub Checks.
3. Diff/context acquisition and the first high-signal deterministic rule pack.
4. Transparent verdict engine and completed GitHub Checks.
5. Scan detail, finding evidence, reports, and repository history.
6. Deterministic suggested patches, decisions, exceptions, and audit events.
7. Reliability, security, performance, and launch-metric instrumentation.

The existing Streamlit application remains the free demo until the GitHub workflow meets these acceptance criteria.
