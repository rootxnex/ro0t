import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import os

# Page configuration
st.set_page_config(
    page_title="Cockerel Shield - Cybersecurity Scanner",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .scan-button {
        background-color: #ff4b4b;
        color: white;
        padding: 0.5rem 2rem;
        border-radius: 0.5rem;
        border: none;
        font-size: 1.2rem;
        font-weight: bold;
    }
    .vulnerability-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid;
    }
    .high-severity { border-left-color: #ff4b4b; }
    .medium-severity { border-left-color: #ffa500; }
    .low-severity { border-left-color: #00ff00; }
</style>
""", unsafe_allow_html=True)

# API configuration
API_BASE_URL = "http://localhost:8000"

def get_severity_color(severity):
    """Get color for severity level"""
    colors = {
        "High": "#ff4b4b",
        "Medium": "#ffa500", 
        "Low": "#00ff00"
    }
    return colors.get(severity, "#666666")

def scan_software(filename):
    """Call the FastAPI backend to scan software"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/scan",
            json={"filename": filename}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to connect to backend API: {str(e)}")
        return None

def get_scan_history():
    """Get scan history from backend"""
    try:
        response = requests.get(f"{API_BASE_URL}/scan-history")
        response.raise_for_status()
        return response.json().get("scans", [])
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to retrieve scan history: {str(e)}")
        return []

def create_severity_chart(vulnerabilities):
    """Create pie chart for severity distribution"""
    if not vulnerabilities:
        return None
    
    # Count vulnerabilities by severity
    severity_counts = {}
    for vuln in vulnerabilities:
        severity = vuln.get("severity", "Unknown")
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    # Create pie chart
    fig = px.pie(
        values=list(severity_counts.values()),
        names=list(severity_counts.keys()),
        title="Vulnerability Severity Distribution",
        color_discrete_map={
            "High": "#ff4b4b",
            "Medium": "#ffa500",
            "Low": "#00ff00"
        }
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=400)
    
    return fig

def display_vulnerability_table(vulnerabilities):
    """Display vulnerabilities in a formatted table"""
    if not vulnerabilities:
        st.info("No vulnerabilities found.")
        return
    
    # Create DataFrame for better display
    vuln_data = []
    for vuln in vulnerabilities:
        vuln_data.append({
            "Vulnerability ID": vuln.get("vuln_id", ""),
            "CVE ID": vuln.get("cve_id", "N/A"),
            "Severity": vuln.get("severity", ""),
            "Description": vuln.get("description", ""),
            "Affected Component": vuln.get("affected_component", "N/A")
        })
    
    df = pd.DataFrame(vuln_data)
    
    # Display with custom styling
    st.markdown("### 📊 Vulnerability Results")
    
    for _, row in df.iterrows():
        severity = row["Severity"]
        severity_class = f"{severity.lower()}-severity"
        
        st.markdown(f"""
        <div class="vulnerability-card {severity_class}">
            <strong>{row['Vulnerability ID']}</strong> ({row['CVE ID']}) - 
            <span style="color: {get_severity_color(severity)}; font-weight: bold;">{severity}</span><br>
            <strong>Component:</strong> {row['Affected Component']}<br>
            <strong>Description:</strong> {row['Description']}
        </div>
        """, unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">🛡️ Cockerel Shield</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Advanced Cybersecurity Vulnerability Scanner</p>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("🔧 Controls")
    st.sidebar.markdown("---")
    
    # File upload section
    st.markdown("## 📁 Upload Software for Scanning")
    
    uploaded_file = st.file_uploader(
        "Choose a file to scan",
        type=['py', 'js', 'php', 'java', 'cpp', 'c', 'html', 'css', 'txt', 'zip', 'tar', 'gz'],
        help="Upload software files for vulnerability analysis"
    )
    
    # Scan button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        scan_button = st.button(
            "🔍 Scan Now",
            type="primary",
            use_container_width=True,
            help="Start vulnerability scan of uploaded software"
        )
    
    # Main content area
    if uploaded_file is not None:
        st.success(f"✅ File uploaded: {uploaded_file.name} ({uploaded_file.size} bytes)")
        
        # Display file info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("File Name", uploaded_file.name)
        with col2:
            st.metric("File Size", f"{uploaded_file.size:,} bytes")
        with col3:
            st.metric("File Type", uploaded_file.type or "Unknown")
    
    # Handle scan button click
    if scan_button and uploaded_file is not None:
        with st.spinner("🔍 Scanning for vulnerabilities..."):
            # Call backend API
            scan_result = scan_software(uploaded_file.name)
            
            if scan_result:
                st.success("✅ Scan completed successfully!")
                
                # Display scan metadata
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Scan ID", scan_result["scan_id"][:8] + "...")
                with col2:
                    st.metric("Total Vulnerabilities", scan_result["total_vulnerabilities"])
                with col3:
                    st.metric("Scan Time", datetime.fromisoformat(scan_result["timestamp"]).strftime("%H:%M:%S"))
                with col4:
                    st.metric("Status", "Completed")
                
                # Create two columns for results
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    # Display vulnerability table
                    display_vulnerability_table(scan_result["vulnerabilities"])
                
                with col2:
                    # Display severity chart
                    st.markdown("### 📈 Severity Distribution")
                    chart = create_severity_chart(scan_result["vulnerabilities"])
                    if chart:
                        st.plotly_chart(chart, use_container_width=True)
                    else:
                        st.info("No data available for chart")
                
                # Store result in session state for history
                if "scan_history" not in st.session_state:
                    st.session_state.scan_history = []
                st.session_state.scan_history.append(scan_result)
                
            else:
                st.error("❌ Scan failed. Please check the backend connection.")
    
    elif scan_button and uploaded_file is None:
        st.warning("⚠️ Please upload a file before scanning.")
    
    # Scan History Section
    st.markdown("---")
    st.markdown("## 📋 Scan History")
    
    # Get scan history from backend
    scan_history = get_scan_history()
    
    if scan_history:
        # Display recent scans
        for scan in scan_history[-5:]:  # Show last 5 scans
            with st.expander(f"Scan: {scan['filename']} - {scan['timestamp'][:19]}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Scan ID:** {scan['scan_id'][:8]}...")
                with col2:
                    st.write(f"**Vulnerabilities:** {scan['total_vulnerabilities']}")
                with col3:
                    st.write(f"**Time:** {scan['timestamp'][:19]}")
                
                # Show vulnerabilities summary
                if scan['vulnerabilities']:
                    severity_summary = {}
                    for vuln in scan['vulnerabilities']:
                        severity = vuln['severity']
                        severity_summary[severity] = severity_summary.get(severity, 0) + 1
                    
                    st.write("**Severity Summary:**")
                    for severity, count in severity_summary.items():
                        st.write(f"- {severity}: {count}")
    else:
        st.info("No scan history available. Run your first scan to see results here.")

if __name__ == "__main__":
    main() 