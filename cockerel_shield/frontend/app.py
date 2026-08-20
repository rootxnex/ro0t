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

st.set_page_config(page_title="Cocokerel Shield", page_icon="🛡️", layout="wide")
st.markdown("""
<style>
:root {--surface:#15243a;--light:#294462;--dark:#07111f;--cyan:#38e8d0;--cyan2:#22c7b5;--ink:#f4f9ff;--muted:#b3c4d8;--danger:#ff6b81;--warning:#ffc857}
.stApp {background:radial-gradient(circle at 85% 0%,#1d3855 0,transparent 32%),linear-gradient(145deg,#0d1929,#14263b);color:var(--ink)}
.stApp h1,.stApp h2,.stApp h3,.stApp h4,.stApp h5,.stApp h6,.stApp p,.stApp label,.stApp li,.stApp small,.stApp [data-testid="stCaptionContainer"] {color:var(--ink)!important}
.stApp [data-testid="stCaptionContainer"],.stApp [data-testid="stCaptionContainer"] p {color:var(--muted)!important}
[data-testid="stSidebar"] {background:#101e31;border-right:1px solid #29425e;box-shadow:8px 0 22px #050b1499}
[data-testid="stSidebar"] * {color:var(--ink)}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {color:var(--muted)!important}
.block-container {max-width:1180px;padding-top:2.4rem}
.hero {padding:2.6rem;border:1px solid #294866;border-radius:28px;background:linear-gradient(145deg,#19304a,#0f1d30);box-shadow:14px 14px 30px #06101dcc,-10px -10px 24px #29476677;margin-bottom:2.2rem}
.hero h1 {margin:0;color:var(--ink);font-size:clamp(2.25rem,5vw,4rem);line-height:1.05;letter-spacing:-.04em}
.hero p {color:var(--muted);margin:.9rem 0 0;max-width:720px;font-size:1.08rem;line-height:1.7}
.badge {display:inline-block;color:#071b21;background:linear-gradient(135deg,var(--cyan),var(--cyan2));border-radius:999px;padding:.38rem .85rem;margin-bottom:1.1rem;font-size:.76rem;font-weight:800;letter-spacing:.08em;box-shadow:0 5px 16px #22c7b544}
[data-testid="stFileUploaderDropzone"] {background:#101f33;border:1px solid #294866;border-radius:22px;box-shadow:inset 7px 7px 14px #07111f,inset -7px -7px 14px #27445f;padding:1.5rem}
[data-testid="stFileUploaderDropzone"] * {color:var(--ink)!important}
[data-testid="stFileUploaderDropzone"] small {color:var(--muted)!important}
[data-testid="stFileUploaderDropzone"] button {background:#e8f2ff!important;color:#102036!important;border:0!important;box-shadow:none!important}
[data-testid="stMetric"] {background:linear-gradient(145deg,#1a3049,#101e31);border:1px solid #29445f;padding:1.15rem;border-radius:20px;box-shadow:8px 8px 18px #07111fcc,-6px -6px 15px #29476655}
.stButton>button,.stDownloadButton>button {border:1px solid #31516d!important;border-radius:16px!important;background:linear-gradient(145deg,#1b344d,#102036)!important;color:var(--ink)!important;box-shadow:6px 6px 13px #06101d,-5px -5px 12px #294766aa!important;transition:all .18s ease}
.stButton>button:hover,.stDownloadButton>button:hover {border-color:var(--cyan)!important;color:var(--cyan)!important;transform:translateY(-1px)}
.stButton>button:disabled,.stDownloadButton>button:disabled {background:#172a40!important;color:#8da3ba!important;border-color:#29445f!important;opacity:1!important;box-shadow:inset 3px 3px 8px #07111f!important}
.stButton>button:disabled *,.stDownloadButton>button:disabled * {color:#8da3ba!important}
.stButton>button:active,.stDownloadButton>button:active {box-shadow:inset 4px 4px 9px #09111e,inset -4px -4px 9px #263b5d!important;transform:none}
[data-baseweb="notification"],[data-testid="stExpander"] {border:1px solid #29445f!important;border-radius:18px!important;background:#112137!important;box-shadow:6px 6px 14px #07111f99,-4px -4px 12px #29476644}
[data-testid="stTextInput"] input {background:#0e1d30;color:var(--ink)!important;border:1px solid #577b9b;border-radius:14px}
[data-testid="stTextInput"] input::placeholder {color:#7891aa!important;opacity:1}
[data-testid="stTextInput"] input:focus {border-color:var(--cyan);box-shadow:0 0 0 1px var(--cyan)}
[role="radiogroup"] label {border-radius:14px;padding:.35rem .6rem;margin:.2rem 0}
[role="radiogroup"] label:has(input:checked) {background:#203957;box-shadow:inset 3px 3px 7px #0a111d,inset -3px -3px 7px #365574}
[role="radiogroup"] label:has(input:checked) p {color:var(--cyan)!important;font-weight:700}
[data-testid="stCheckbox"] label span,[data-testid="stCheckbox"] label p {color:var(--ink)!important}
hr {border-color:#263a55!important}.footer {color:#7890aa;text-align:center;padding:2.5rem 0 1rem}
</style>
""", unsafe_allow_html=True)


def scan_page() -> None:
    st.markdown("""
    <section class="hero"><span class="badge">FREE · LOCAL-FIRST · OPEN SOURCE</span>
    <h1>Find risky code before it ships.</h1>
    <p>Cocokerel Shield scans source files for high-signal code execution and secret patterns.
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
    downloads[0].download_button("Download JSON", json_report(result), "cocokerel-shield-report.json", "application/json", use_container_width=True)
    downloads[1].download_button("Download Markdown", markdown_report(result), "cocokerel-shield-report.md", "text/markdown", use_container_width=True)

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
            st.download_button("Download JSON", json_report(result), f"cocokerel-shield-{result.scan_id[:8]}.json", "application/json")


def about_page() -> None:
    st.title("About Cocokerel Shield")
    st.write("Cocokerel Shield is a deterministic, local-first source scanner. It does not use AI to invent findings, call a paid API, execute uploaded files, or retain uploads.")
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


st.sidebar.title("🛡️ Cocokerel Shield")
page = st.sidebar.radio("Navigate", ["Scanner", "History", "About"], label_visibility="collapsed")
st.sidebar.divider()
st.sidebar.success("No API key or paid service required")
st.sidebar.caption("Deterministic scanner · v0.1.0")
{"Scanner": scan_page, "History": history_page, "About": about_page}[page]()
st.markdown('<div class="footer">Cocokerel Shield · Built for transparent security checks</div>', unsafe_allow_html=True)
