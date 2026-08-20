from __future__ import annotations

import ipaddress
import socket
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from dataclasses import dataclass
from io import BytesIO

from .engine import ScanResult
from .uploads import MAX_FILE_BYTES, MAX_FILES, MAX_TOTAL_BYTES, UploadedSource, scan_uploads

MAX_DOWNLOAD_BYTES = 12_000_000
ALLOWED_SOURCE_SUFFIXES = {".py", ".js", ".jsx", ".ts", ".tsx", ".php", ".java", ".cpp", ".c", ".h", ".html", ".xml", ".json", ".yaml", ".yml", ".toml", ".env"}


class LinkScanError(ValueError):
    pass


@dataclass(frozen=True)
class WebCheck:
    severity: str
    title: str
    detail: str


@dataclass(frozen=True)
class WebsiteReport:
    url: str
    status: int
    checks: tuple[WebCheck, ...]


def scan_github_repository(url: str) -> ScanResult:
    owner, repo, branch = _github_parts(url)
    archive_url = f"https://codeload.github.com/{owner}/{repo}/zip/refs/heads/{branch}"
    payload, _, _, _ = _fetch(archive_url, method="GET", max_bytes=MAX_DOWNLOAD_BYTES)
    uploads: list[UploadedSource] = []
    total = 0
    try:
        archive = zipfile.ZipFile(BytesIO(payload))
        for item in archive.infolist():
            if item.is_dir() or item.file_size > MAX_FILE_BYTES:
                continue
            suffix = "." + item.filename.rsplit(".", 1)[-1].lower() if "." in item.filename else ""
            if suffix not in ALLOWED_SOURCE_SUFFIXES:
                continue
            if len(uploads) >= MAX_FILES or total + item.file_size > MAX_TOTAL_BYTES:
                break
            content = archive.read(item)
            total += len(content)
            safe_name = item.filename.replace("/", "__")[-240:]
            uploads.append(UploadedSource(safe_name, content))
    except (zipfile.BadZipFile, OSError) as error:
        raise LinkScanError("GitHub returned an invalid repository archive") from error
    if not uploads:
        raise LinkScanError("No supported source files were found on that branch")
    return scan_uploads(uploads)


def scan_website(url: str) -> WebsiteReport:
    normalized = _public_url(url)
    try:
        _, final_url, status, response_headers = _fetch(normalized, method="HEAD", max_bytes=0)
    except LinkScanError as error:
        if "HTTP 405" not in str(error):
            raise
        _, final_url, status, response_headers = _fetch(normalized, method="GET", max_bytes=65_536)
    headers = {key.lower(): value for key, value in response_headers.items()}
    checks: list[WebCheck] = []
    if urllib.parse.urlsplit(final_url).scheme != "https":
        checks.append(WebCheck("HIGH", "HTTPS is not enforced", "The final response uses unencrypted HTTP."))
    expected = {
        "strict-transport-security": ("MEDIUM", "HSTS header is missing", "Add Strict-Transport-Security after HTTPS is fully enabled."),
        "content-security-policy": ("MEDIUM", "Content Security Policy is missing", "Add a restrictive Content-Security-Policy to reduce script injection impact."),
        "x-content-type-options": ("LOW", "MIME sniffing protection is missing", "Set X-Content-Type-Options: nosniff."),
        "referrer-policy": ("LOW", "Referrer policy is missing", "Set a privacy-preserving Referrer-Policy."),
        "permissions-policy": ("LOW", "Permissions policy is missing", "Restrict browser capabilities with Permissions-Policy."),
    }
    for name, finding in expected.items():
        if name not in headers:
            checks.append(WebCheck(*finding))
    server = headers.get("server")
    if server:
        checks.append(WebCheck("INFO", "Server software is disclosed", f"The Server header exposes: {server[:100]}"))
    cookie = headers.get("set-cookie", "")
    if cookie and "secure" not in cookie.lower():
        checks.append(WebCheck("MEDIUM", "Cookie lacks Secure", "At least one response cookie may be sent without the Secure attribute."))
    if cookie and "httponly" not in cookie.lower():
        checks.append(WebCheck("LOW", "Cookie lacks HttpOnly", "At least one response cookie may be readable by client-side scripts."))
    return WebsiteReport(final_url, status, tuple(checks))


def _github_parts(value: str) -> tuple[str, str, str]:
    parsed = urllib.parse.urlsplit(value.strip())
    if parsed.scheme != "https" or parsed.hostname not in {"github.com", "www.github.com"}:
        raise LinkScanError("Use a public HTTPS GitHub repository URL")
    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) < 2:
        raise LinkScanError("GitHub URL must include an owner and repository")
    owner, repo = parts[0], parts[1].removesuffix(".git")
    branch = parts[3] if len(parts) >= 4 and parts[2] == "tree" else "main"
    if not all(part.replace("-", "").replace("_", "").replace(".", "").isalnum() for part in (owner, repo, branch)):
        raise LinkScanError("GitHub owner, repository, or branch is invalid")
    return owner, repo, branch


def _public_url(value: str) -> str:
    parsed = urllib.parse.urlsplit(value.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password:
        raise LinkScanError("Enter a valid public HTTP or HTTPS URL")
    if parsed.port and parsed.port not in {80, 443}:
        raise LinkScanError("Only standard web ports 80 and 443 are allowed")
    try:
        addresses = {item[4][0] for item in socket.getaddrinfo(parsed.hostname, parsed.port or 443)}
    except socket.gaierror as error:
        raise LinkScanError("The hostname could not be resolved") from error
    if any(not ipaddress.ip_address(address).is_global for address in addresses):
        raise LinkScanError("Private, local, and reserved network addresses are not allowed")
    return urllib.parse.urlunsplit(parsed)


def _fetch(url: str, *, method: str, max_bytes: int, redirects: int = 3):
    current = url
    opener = urllib.request.build_opener(_NoRedirect())
    for _ in range(redirects + 1):
        current = _public_url(current)
        request = urllib.request.Request(current, method=method, headers={"User-Agent": "Cockerel-Shield/0.1 passive-security-check"})
        try:
            response = opener.open(request, timeout=10)
        except urllib.error.HTTPError as error:
            if error.code in {301, 302, 303, 307, 308} and error.headers.get("Location"):
                current = urllib.parse.urljoin(current, error.headers["Location"])
                continue
            raise LinkScanError(f"The remote server returned HTTP {error.code}") from error
        except (urllib.error.URLError, TimeoutError) as error:
            raise LinkScanError("The remote server could not be reached") from error
        length = int(response.headers.get("Content-Length", "0") or 0)
        if max_bytes and length > max_bytes:
            raise LinkScanError("The remote content exceeds the scan limit")
        payload = response.read(max_bytes + 1) if max_bytes else b""
        if max_bytes and len(payload) > max_bytes:
            raise LinkScanError("The remote content exceeds the scan limit")
        return payload, current, response.status, response.headers
    raise LinkScanError("Too many redirects")


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None
