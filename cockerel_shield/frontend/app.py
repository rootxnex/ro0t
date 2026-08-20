from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from cshield.models import Severity
from cshield.linkscan import LinkScanError, WebsiteReport, scan_github_repository, scan_website
from cshield.reporting import json_report, markdown_report
from cshield.uploads import UploadError, UploadedSource, scan_uploads

st.set_page_config(page_title="Cockerel Shield", page_icon="🛡️", layout="wide")
st.markdown("""
<style>
:root {--surface:#172235;--light:#22324c;--dark:#0a111d;--mint:#5eead4;--ink:#edf6ff;--muted:#9cb0c8}
.stApp {background:linear-gradient(145deg,#111c2d,#17253a);color:var(--ink)}
[data-testid="stSidebar"] {background:#142033;border-right:0;box-shadow:8px 0 22px #0a111d99}
.block-container {max-width:1180px;padding-top:2.4rem}
.hero {padding:2.6rem;border:0;border-radius:28px;background:linear-gradient(145deg,#1a2940,#121d30);box-shadow:14px 14px 30px #09111ecc,-10px -10px 24px #263b5d88;margin-bottom:2.2rem}
.hero h1 {margin:0;color:var(--ink);font-size:clamp(2.25rem,5vw,4rem);line-height:1.05;letter-spacing:-.04em}
.hero p {color:var(--muted);margin:.9rem 0 0;max-width:720px;font-size:1.08rem;line-height:1.7}
.badge {display:inline-block;color:var(--mint);background:#142538;border-radius:999px;padding:.38rem .85rem;margin-bottom:1.1rem;font-size:.76rem;font-weight:700;letter-spacing:.08em;box-shadow:inset 3px 3px 7px #09111e,inset -3px -3px 7px #263b5d}
[data-testid="stFileUploaderDropzone"] {background:#142033;border:0;border-radius:22px;box-shadow:inset 7px 7px 14px #0a111d,inset -7px -7px 14px #223651;padding:1.5rem}
[data-testid="stMetric"] {background:linear-gradient(145deg,#19273c,#121d2e);border:0;padding:1.15rem;border-radius:20px;box-shadow:8px 8px 18px #0a111dcc,-6px -6px 15px #263b5d66}
.stButton>button,.stDownloadButton>button {border:0!important;border-radius:16px!important;background:linear-gradient(145deg,#1d3047,#142135)!important;color:var(--ink)!important;box-shadow:6px 6px 13px #09111e,-5px -5px 12px #263b5d!important;transition:all .18s ease}
.stButton>button:hover,.stDownloadButton>button:hover {color:var(--mint)!important;transform:translateY(-1px)}
.stButton>button:active,.stDownloadButton>button:active {box-shadow:inset 4px 4px 9px #09111e,inset -4px -4px 9px #263b5d!important;transform:none}
[data-baseweb="notification"],[data-testid="stExpander"] {border:0!important;border-radius:18px!important;background:#152236!important;box-shadow:6px 6px 14px #0a111d99,-4px -4px 12px #263b5d55}
[role="radiogroup"] label {border-radius:14px;padding:.35rem .6rem;margin:.2rem 0}
[role="radiogroup"] label:has(input:checked) {background:#1b2b42;box-shadow:inset 3px 3px 7px #0a111d,inset -3px -3px 7px #263b5d}
hr {border-color:#263a55!important}.footer {color:#7890aa;text-align:center;padding:2.5rem 0 1rem}
</style>
""", unsafe_allow_html=True)


def scan_page() -> None:
    st.markdown("""
    <section class="hero"><span class="badge">FREE · LOCAL-FIRST · OPEN SOURCE</span>
    <h1>Find risky code before it ships.</h1>
    <p>Cockerel Shield scans source files for high-signal code execution and secret patterns.
    Files are processed only for this scan and are never executed.</p></section>
    """, unsafe_allow_html=True)

    left, right = st.columns([3, 2], gap="large")
    with left:
        st.subheader("Start a scan")
        uploads = st.file_uploader(
            "Drop source files here",
            type=["py", "js", "jsx", "ts", "tsx", "php", "java", "cpp", "c", "h", "html", "xml", "json", "yaml", "yml", "toml", "env"],
            accept_multiple_files=True,
            help="Maximum 100 files, 1 MB per file, and 10 MB per scan. Archives are disabled.",
        )
        if uploads:
            st.caption(f"{len(uploads)} file(s) · {sum(item.size for item in uploads) / 1024:.1f} KB")
        run_scan = st.button("Scan files", type="primary", disabled=not uploads, use_container_width=True)
    with right:
        st.subheader("What this checks")
        st.markdown("""
        - Dynamic Python and JavaScript execution
        - Python subprocess calls using a shell
        - Committed private-key material
        - Likely hard-coded API credentials

        Results include evidence, CWE mapping, confidence, and remediation.
        """)
        st.warning("This focused baseline is not a replacement for a full security review.")

    st.divider()
    st.subheader("Scan from a link")
    st.caption("Public GitHub repositories receive source analysis. Other websites receive passive configuration checks only.")
    link = st.text_input("Public GitHub repository or website URL", placeholder="https://github.com/owner/repository or https://example.com")
    authorized = st.checkbox("I own this target or have permission to assess it.")
    scan_link = st.button("Scan link", disabled=not (link and authorized), use_container_width=True)
    if scan_link:
        try:
            with st.spinner("Running bounded security checks…"):
                if link.lower().startswith(("https://github.com/", "https://www.github.com/")):
                    result = scan_github_repository(link)
                    st.session_state.latest_scan = result
                    history = st.session_state.setdefault("scan_history", [])
                    history.insert(0, result)
                    del history[10:]
                    st.session_state.pop("website_report", None)
                else:
                    st.session_state.website_report = scan_website(link)
        except LinkScanError as error:
            st.error(str(error))

    website_report: WebsiteReport | None = st.session_state.get("website_report")
    if website_report:
        st.markdown(f"#### Passive website report · HTTP {website_report.status}")
        st.caption(website_report.url)
        if not website_report.checks:
            st.success("No issues were identified by the configured passive checks.")
        for check in website_report.checks:
            with st.expander(f"{check.severity} · {check.title}"):
                st.write(check.detail)

    if run_scan:
        try:
            with st.spinner("Inspecting source without executing it…"):
                result = scan_uploads(UploadedSource(item.name, item.getvalue()) for item in uploads)
            st.session_state.latest_scan = result
            history = st.session_state.setdefault("scan_history", [])
            history.insert(0, result)
            del history[10:]
        except UploadError as error:
            st.error(str(error))

    result = st.session_state.get("latest_scan")
    if result is None:
        st.info("Upload one or more source files to generate an evidence-based report.")
        return

    st.divider()
    st.subheader("Latest report")
    counts = Counter(finding.severity for finding in result.findings)
    metrics = st.columns(5)
    for column, label, value in zip(metrics, ["Files", "Findings", "Critical", "High", "Skipped"],
                                    [result.files_scanned, len(result.findings), counts[Severity.CRITICAL], counts[Severity.HIGH], result.files_skipped]):
        column.metric(label, value)

    downloads = st.columns(2)
    downloads[0].download_button("Download JSON", json_report(result), "cockerel-shield-report.json", "application/json", use_container_width=True)
    downloads[1].download_button("Download Markdown", markdown_report(result), "cockerel-shield-report.md", "text/markdown", use_container_width=True)

    if not result.findings:
        st.success("No configured rules matched. This does not guarantee the code is vulnerability-free.")
    for finding in result.findings:
        with st.expander(f"{finding.severity.value} · {finding.title} · {finding.file}:{finding.start_line}", expanded=True):
            st.caption(f"Confidence: {finding.confidence.value} · Rule: {finding.rule_id} · {', '.join(finding.cwe)}")
            st.write(finding.description)
            st.markdown("**Evidence**")
            st.code(finding.evidence[0].snippet, language=None)
            st.markdown("**Defensive scenario**")
            st.write(finding.attack_scenario)
            st.markdown("**How to fix it**")
            st.write(finding.remediation)


def history_page() -> None:
    st.title("Session history")
    st.caption("History stays in this browser session and is not written to a database.")
    history = st.session_state.get("scan_history", [])
    if not history:
        st.info("No scans have been run in this session.")
    for result in history:
        with st.expander(f"{result.started_at} · {result.files_scanned} files · {len(result.findings)} findings"):
            st.code(result.scan_id)
            st.download_button("Download JSON", json_report(result), f"cockerel-shield-{result.scan_id[:8]}.json", "application/json")


def about_page() -> None:
    st.title("About Cockerel Shield")
    st.write("Cockerel Shield is a deterministic, local-first source scanner. It does not use AI to invent findings, call a paid API, execute uploaded files, or retain uploads.")
    st.subheader("Trust boundaries")
    st.markdown("""
    - Uploads are limited by count and size and written only to a temporary directory.
    - Filenames containing paths are rejected.
    - Findings are produced by versioned regular-expression rules.
    - Secret evidence is redacted in reports.
    - Website checks send one passive request and never exploit or bypass controls.
    - Link targets must resolve to public networks; local and private addresses are blocked.
    """)
    st.caption("Licensed under MIT. Review the repository threat model before production use.")


st.sidebar.title("🛡️ Cockerel Shield")
page = st.sidebar.radio("Navigate", ["Scanner", "History", "About"], label_visibility="collapsed")
st.sidebar.divider()
st.sidebar.success("No API key or paid service required")
st.sidebar.caption("Deterministic scanner · v0.1.0")
{"Scanner": scan_page, "History": history_page, "About": about_page}[page]()
st.markdown('<div class="footer">Cockerel Shield · Built for transparent security checks</div>', unsafe_allow_html=True)
