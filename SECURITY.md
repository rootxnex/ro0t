# Security Policy

## Supported versions

Only the latest commit on the default branch is currently supported. Cockerel Shield is pre-release software and must not be treated as a substitute for security review.

## Reporting a vulnerability

Please use GitHub's private vulnerability-reporting feature for this repository. Do not include live credentials, personal data, or exploit traffic against systems you do not own. Include the affected revision, reproduction steps, impact, and any suggested mitigation.

Maintainers should acknowledge a report within seven days, provide a status update within fourteen days, and coordinate disclosure after a fix is available. Please do not open a public issue for an unpatched vulnerability.

## Scope and safe testing

Testing is authorized only against code and systems you own or have explicit permission to assess. The local scanner is designed to read repository content without executing it. See `cockerel_shield/THREAT_MODEL.md` for current trust boundaries and limitations.
