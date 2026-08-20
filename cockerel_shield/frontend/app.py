from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from cshield.models import Severity
from cshield.reporting import json_report, markdown_report
from cshield.uploads import UploadError, UploadedSource, scan_uploads

st.set_page_config(page_title="Cockerel Shield", page_icon="🛡️", layout="wide")
st.markdown("""
<style>
.stApp {background:#08111f} [data-testid="stSidebar"] {background:#0d1a2b}
.hero {padding:2rem;border:1px solid #1e3a5f;border-radius:18px;background:linear-gradient(135deg,#0d1a2b,#102942);margin-bottom:1.5rem}
.hero h1 {margin:0;color:#f8fafc}.hero p {color:#a8c0dc;margin:.55rem 0 0;max-width:760px}
.badge {display:inline-block;color:#5eead4;background:#0f3b40;border:1px solid #17626a;border-radius:999px;padding:.2rem .65rem;margin-bottom:.8rem;font-size:.82rem}
[data-testid="stMetric"] {background:#0d1a2b;border:1px solid #1e3a5f;padding:1rem;border-radius:14px}
.footer {color:#6f89a5;text-align:center;padding:2rem 0 1rem}
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
    """)
    st.caption("Licensed under MIT. Review the repository threat model before production use.")


st.sidebar.title("🛡️ Cockerel Shield")
page = st.sidebar.radio("Navigate", ["Scanner", "History", "About"], label_visibility="collapsed")
st.sidebar.divider()
st.sidebar.success("No API key or paid service required")
st.sidebar.caption("Deterministic scanner · v0.1.0")
{"Scanner": scan_page, "History": history_page, "About": about_page}[page]()
st.markdown('<div class="footer">Cockerel Shield · Built for transparent security checks</div>', unsafe_allow_html=True)
