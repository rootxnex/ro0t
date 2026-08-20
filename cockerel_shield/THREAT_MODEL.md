# Threat model

## Trust boundaries

The user selects a repository. Cocokerel Shield reads that untrusted repository, invokes configured scanner adapters, normalizes their untrusted output, and writes findings to user-selected output. Future AI providers are a separate outbound trust boundary.

## Principal threats and MVP controls

| Threat | Current control | Remaining work |
|---|---|---|
| Repository code execution | Scanner only reads files; it never imports, builds, or executes repository content | Sandbox external scanner processes |
| Path/symlink escape | Canonical root, no symlink following, symlink files skipped | Add archive extraction policy before archive support |
| Resource exhaustion | 1 MB per-file limit and common generated/vendor directories excluded | Add total byte/file/time budgets |
| Secret disclosure | Secret evidence is redacted in reports | Redact third-party adapter output and encrypt stored raw output |
| Malicious filenames | Paths are handled as `Path` values; no shell command construction | Escape filenames in every future renderer/UI |
| Prompt injection | No AI module exists; repository content is treated only as data | Isolate and delimit code if AI is explicitly enabled |
| Scanner compromise | No external scanners are invoked in this milestone | Pin binaries, pass argument arrays, enforce timeouts and resource limits |
| Unauthorized access | CLI is local-only | Add authentication and per-project authorization before hosted scans |
| SSRF | No remote fetch or URL scanning exists | Allow-list Git schemes/hosts and block internal destinations later |

Out of scope: active target scanning, repository code execution, autonomous exploitation, and automatic transmission of code to AI services.
