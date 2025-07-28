import streamlit as st
import requests
import pandas as pd
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
import os
import time
import math
from datetime import datetime, timedelta
import random

# --- Enhanced Branding Colors ---
NAVY = "#0A1F44"
TEAL = "#00B8D9"
GRAY = "#E0E0E0"
DARK_GRAY = "#1a1a1a"
LIGHT_GRAY = "#2d2d2d"
WHITE = "#FFFFFF"
SUCCESS_GREEN = "#00D4AA"
WARNING_ORANGE = "#FF6B35"
ERROR_RED = "#FF4757"
INFO_BLUE = "#3742FA"
PURPLE = "#5F27CD"

st.set_page_config(
    page_title="Cockerel Shield - AI Cyber Defense",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Enhanced Custom CSS for Modern Dark Theme ---
st.markdown(f"""
<style>
    /* Main background */
    .main {{
        background: linear-gradient(135deg, {DARK_GRAY} 0%, #2d2d2d 100%);
        color: {WHITE};
    }}
    
    /* Sidebar */
    .css-1d391kg {{
        background: linear-gradient(180deg, {NAVY} 0%, #1a2a4a 100%);
        border-right: 1px solid {TEAL};
    }}
    
    /* Title bar with gradient */
    .title-bar {{
        background: linear-gradient(90deg, {NAVY} 0%, {TEAL} 100%);
        color: {WHITE};
        padding: 20px;
        font-size: 28px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 25px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 4px 15px rgba(0, 184, 217, 0.3);
        border: 1px solid {TEAL};
    }}
    
    /* Enhanced Cards with hover effects */
    .metric-card {{
        background: linear-gradient(145deg, {LIGHT_GRAY} 0%, #3a3a3a 100%);
        padding: 25px;
        border-radius: 15px;
        border-left: 5px solid {TEAL};
        margin: 15px 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
        border: 1px solid #404040;
    }}
    
    .metric-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 184, 217, 0.2);
        border-left: 5px solid {SUCCESS_GREEN};
    }}
    
    /* Enhanced Buttons */
    .stButton > button {{
        background: linear-gradient(45deg, {TEAL} 0%, {INFO_BLUE} 100%);
        color: {WHITE};
        font-weight: bold;
        padding: 12px 24px;
        border: none;
        border-radius: 8px;
        transition: all 0.3s ease;
        box-shadow: 0 2px 10px rgba(0, 184, 217, 0.3);
    }}
    
    .stButton > button:hover {{
        transform: translateY(-1px);
        box-shadow: 0 4px 15px rgba(0, 184, 217, 0.5);
    }}
    
    /* Status indicators with better colors */
    .status-healthy {{ color: {SUCCESS_GREEN}; font-weight: bold; }}
    .status-vulnerable {{ color: {WARNING_ORANGE}; font-weight: bold; }}
    .status-compromised {{ color: {ERROR_RED}; font-weight: bold; }}
    .status-critical {{ color: {ERROR_RED}; font-weight: bold; }}
    .status-high {{ color: {ERROR_RED}; font-weight: bold; }}
    .status-medium {{ color: {WARNING_ORANGE}; font-weight: bold; }}
    .status-low {{ color: {SUCCESS_GREEN}; font-weight: bold; }}
    
    /* Enhanced Search bar */
    .search-container {{
        background: linear-gradient(145deg, {LIGHT_GRAY} 0%, #3a3a3a 100%);
        padding: 15px;
        border-radius: 12px;
        margin: 15px 0;
        border: 1px solid {TEAL};
        box-shadow: 0 2px 10px rgba(0, 184, 217, 0.1);
    }}
    
    /* Enhanced Tables */
    .dataframe {{
        background: linear-gradient(145deg, {LIGHT_GRAY} 0%, #3a3a3a 100%);
        color: {WHITE};
        border-radius: 8px;
        border: 1px solid #404040;
    }}
    
    /* Enhanced Tabs */
    .stTabs [data-baseweb="tab"] {{
        background: linear-gradient(145deg, {LIGHT_GRAY} 0%, #3a3a3a 100%);
        color: {WHITE};
        font-weight: bold;
        border-radius: 8px 8px 0 0;
        border: 1px solid #404040;
    }}
    
    /* Progress bars with gradient */
    .progress-bar {{
        background: linear-gradient(90deg, {TEAL} 0%, {SUCCESS_GREEN} 100%);
        height: 10px;
        border-radius: 5px;
        margin: 8px 0;
        box-shadow: 0 2px 5px rgba(0, 184, 217, 0.3);
    }}
    
    /* Alert boxes */
    .alert-success {{
        background: linear-gradient(145deg, {SUCCESS_GREEN}20 0%, {SUCCESS_GREEN}10 100%);
        border: 1px solid {SUCCESS_GREEN};
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }}
    
    .alert-warning {{
        background: linear-gradient(145deg, {WARNING_ORANGE}20 0%, {WARNING_ORANGE}10 100%);
        border: 1px solid {WARNING_ORANGE};
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }}
    
    .alert-error {{
        background: linear-gradient(145deg, {ERROR_RED}20 0%, {ERROR_RED}10 100%);
        border: 1px solid {ERROR_RED};
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }}
    
    /* Chart containers */
    .chart-container {{
        background: linear-gradient(145deg, {LIGHT_GRAY} 0%, #3a3a3a 100%);
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #404040;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }}
</style>
""", unsafe_allow_html=True)

# --- Initialize Session State ---
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Dashboard"

# --- Enhanced Mock Data Functions ---
def generate_threat_data():
    """Generate realistic threat data with timestamps and varied severity"""
    base_time = datetime.now()
    threats = [
        {
            "id": f"threat-{int(base_time.timestamp())}-{random.randint(10, 99)}",
            "type": "Phishing",
            "severity": "High",
            "status": "Active",
            "ip": "10.0.0.122",
            "time": (base_time - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S"),
            "description": "Suspicious email with malicious link detected in user inbox",
            "confidence": 96,
            "source": "Email Gateway",
            "affected_users": 3
        },
        {
            "id": f"threat-{int(base_time.timestamp())}-{random.randint(10, 99)}",
            "type": "XSS",
            "severity": "Critical",
            "status": "Resolved",
            "ip": "172.16.0.248",
            "time": (base_time - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
            "description": "Cross-site scripting attempt detected in web application",
            "confidence": 99,
            "source": "Web Application Firewall",
            "affected_users": 0
        },
        {
            "id": f"threat-{int(base_time.timestamp())}-{random.randint(10, 99)}",
            "type": "Brute Force",
            "severity": "Medium",
            "status": "Active",
            "ip": "203.0.113.94",
            "time": (base_time - timedelta(hours=6)).strftime("%Y-%m-%d %H:%M:%S"),
            "description": "Multiple failed login attempts detected from suspicious IP",
            "confidence": 93,
            "source": "Authentication Service",
            "affected_users": 1
        },
        {
            "id": f"threat-{int(base_time.timestamp())}-{random.randint(10, 99)}",
            "type": "SQL Injection",
            "severity": "Critical",
            "status": "Resolved",
            "ip": "192.168.1.72",
            "time": (base_time - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"),
            "description": "Malformed SQL query detected in database access",
            "confidence": 99,
            "source": "Database Monitor",
            "affected_users": 0
        },
        {
            "id": f"threat-{int(base_time.timestamp())}-{random.randint(10, 99)}",
            "type": "DDoS",
            "severity": "Medium",
            "status": "Active",
            "ip": "10.0.0.0",
            "time": (base_time - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"),
            "description": "Unusual traffic spike detected on web servers",
            "confidence": 94,
            "source": "Network Monitor",
            "affected_users": 15
        },
        {
            "id": f"threat-{int(base_time.timestamp())}-{random.randint(10, 99)}",
            "type": "Malware",
            "severity": "High",
            "status": "Active",
            "ip": "198.51.100.45",
            "time": (base_time - timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S"),
            "description": "Suspicious file upload detected with potential malware",
            "confidence": 87,
            "source": "File Upload Scanner",
            "affected_users": 2
        }
    ]
    return threats

def generate_vulnerability_data():
    """Generate realistic vulnerability data with proper categorization"""
    base_time = datetime.now()
    vulns = [
        {
            "id": f"VUL-{random.randint(7000, 7999)}",
            "title": "Authentication Bypass in API Gateway",
            "category": "Authentication",
            "severity": "Critical",
            "status": "Open",
            "bounty": "$5000",
            "reported": (base_time - timedelta(days=2)).strftime("%Y-%m-%d"),
            "cve_id": "CVE-2024-1234",
            "affected_component": "api/auth/verify",
            "cvss_score": 9.8,
            "reporter": "security_researcher_01"
        },
        {
            "id": f"VUL-{random.randint(7000, 7999)}",
            "title": "SQL Injection in User Search Function",
            "category": "Injection",
            "severity": "High",
            "status": "In Review",
            "bounty": "$3500",
            "reported": (base_time - timedelta(days=3)).strftime("%Y-%m-%d"),
            "cve_id": "CVE-2024-5678",
            "affected_component": "search/users.php",
            "cvss_score": 8.5,
            "reporter": "whitehat_hacker"
        },
        {
            "id": f"VUL-{random.randint(7000, 7999)}",
            "title": "Cross-Site Scripting in Comment System",
            "category": "XSS",
            "severity": "Medium",
            "status": "In Review",
            "bounty": "$2000",
            "reported": (base_time - timedelta(days=5)).strftime("%Y-%m-%d"),
            "cve_id": "CVE-2024-9012",
            "affected_component": "comments/display.php",
            "cvss_score": 6.1,
            "reporter": "bug_hunter_2024"
        },
        {
            "id": f"VUL-{random.randint(7000, 7999)}",
            "title": "CSRF Token Missing in Profile Update",
            "category": "CSRF",
            "severity": "Low",
            "status": "Fixed",
            "bounty": "$1000",
            "reported": (base_time - timedelta(days=7)).strftime("%Y-%m-%d"),
            "cve_id": "CVE-2024-3456",
            "affected_component": "profile/update.php",
            "cvss_score": 4.3,
            "reporter": "security_analyst"
        },
        {
            "id": f"VUL-{random.randint(7000, 7999)}",
            "title": "Sensitive Data Exposure in Application Logs",
            "category": "Data Exposure",
            "severity": "Medium",
            "status": "Fixed",
            "bounty": "$1500",
            "reported": (base_time - timedelta(days=10)).strftime("%Y-%m-%d"),
            "cve_id": "CVE-2024-7890",
            "affected_component": "logs/application.log",
            "cvss_score": 5.5,
            "reporter": "penetration_tester"
        },
        {
            "id": f"VUL-{random.randint(7000, 7999)}",
            "title": "Buffer Overflow in File Upload Handler",
            "category": "Memory Corruption",
            "severity": "Critical",
            "status": "Open",
            "bounty": "$7500",
            "reported": (base_time - timedelta(days=1)).strftime("%Y-%m-%d"),
            "cve_id": "CVE-2024-1111",
            "affected_component": "upload/processor.php",
            "cvss_score": 9.1,
            "reporter": "vulnerability_researcher"
        }
    ]
    return vulns

def generate_network_data():
    return {
        "healthy": 6,
        "vulnerable": 1,
        "compromised": 1,
        "total": 8,
        "devices": [
            {"name": "Network Router", "status": "healthy", "type": "router"},
            {"name": "Main Server", "status": "healthy", "type": "server"},
            {"name": "Workstation 1", "status": "healthy", "type": "workstation"},
            {"name": "Workstation 2", "status": "healthy", "type": "workstation"},
            {"name": "Firewall", "status": "healthy", "type": "firewall"},
            {"name": "Infected Client", "status": "compromised", "type": "client"},
            {"name": "Gateway", "status": "vulnerable", "type": "gateway"}
        ]
    }

def generate_log_data():
    logs = [
        {"id": "LOG-9981", "timestamp": "2025-04-13 08:32:17", "level": "ERROR", "source": "Firewall", 
         "category": "network", "message": "Blocked connection attempt from suspicious IP"},
        {"id": "LOG-9982", "timestamp": "2025-04-13 08:30:45", "level": "WARNING", "source": "Auth Service", 
         "category": "authentication", "message": "Multiple failed login attempts detected"},
        {"id": "LOG-9983", "timestamp": "2025-04-13 08:28:12", "level": "INFO", "source": "System", 
         "category": "system", "message": "Automatic update check completed"},
        {"id": "LOG-9984", "timestamp": "2025-04-13 08:25:33", "level": "ERROR", "source": "Database", 
         "category": "database", "message": "Query timeout - possible overload"},
        {"id": "LOG-9985", "timestamp": "2025-04-13 08:22:18", "level": "WARNING", "source": "API Gateway", 
         "category": "api", "message": "Rate limit exceeded for endpoint"},
        {"id": "LOG-9986", "timestamp": "2025-04-13 08:20:05", "level": "INFO", "source": "User Service", 
         "category": "user", "message": "New user registered: jackson.doe"},
        {"id": "LOG-9987", "timestamp": "2025-04-13 08:18:42", "level": "INFO", "source": "CDN", 
         "category": "cdn", "message": "Cache miss for asset/image-123.jpg"},
        {"id": "LOG-9988", "timestamp": "2025-04-13 08:15:29", "level": "ERROR", "source": "Payment Service", 
         "category": "payment", "message": "Failed to process payment for order #12345"},
        {"id": "LOG-9989", "timestamp": "2025-04-13 08:12:11", "level": "INFO", "source": "System", 
         "category": "system", "message": "Backup completed successfully"}
    ]
    return logs

# --- Page Functions ---
def dashboard_page():
    st.markdown('<div class="title-bar">🛡️ Cockerel Shield - AI Cyber Defense</div>', unsafe_allow_html=True)
    
    # Search bar with functionality
    search_query = st.text_input("🔍 Search threats, vulnerabilities, systems...", placeholder="Enter search term...")
    
    # Enhanced Threat Overview with real data
    threats = generate_threat_data()
    threat_counts = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}
    for threat in threats:
        if threat["severity"] in threat_counts:
            threat_counts[threat["severity"]] += 1
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Low</h3>
            <h2 style="color: {SUCCESS_GREEN};">{threat_counts['Low']}</h2>
            <p>Threats</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Medium</h3>
            <h2 style="color: {WARNING_ORANGE};">{threat_counts['Medium']}</h2>
            <p>Threats</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>High</h3>
            <h2 style="color: {ERROR_RED};">{threat_counts['High']}</h2>
            <p>Threats</p>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Critical</h3>
            <h2 style="color: {ERROR_RED};">{threat_counts['Critical']}</h2>
            <p>Threats</p>
        </div>
        """, unsafe_allow_html=True)
    
    total_threats = sum(threat_counts.values())
    st.markdown(f"**{total_threats} Threats detected**")
    
    # Enhanced System Status with alerts
    st.markdown("### 🔧 System Status")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if random.choice([True, False]):
            st.markdown('<div class="alert-success">**Firewall Status** ✅ Active & Filtering</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-warning">**Firewall Status** ⚠️ High Load</div>', unsafe_allow_html=True)
            
    with col2:
        st.markdown('<div class="alert-success">**Intrusion Detection** ✅ Monitoring Active</div>', unsafe_allow_html=True)
        
    with col3:
        vulns = generate_vulnerability_data()
        critical_vulns = len([v for v in vulns if v["severity"] == "Critical"])
        if critical_vulns > 0:
            st.markdown(f'<div class="alert-error">**Vulnerability Scan** ⚠️ {critical_vulns} Critical Findings</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-success">**Vulnerability Scan** ✅ No Critical Issues</div>', unsafe_allow_html=True)
            
    with col4:
        st.markdown('<div class="alert-success">**Last System Update** ⏰ 4h ago (Current)</div>', unsafe_allow_html=True)
    
    # Enhanced AI Defense Module
    st.markdown("### 🤖 AI Defense Module")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("**AI Model Status** 🟢 Active")
        st.markdown("**Last model update** 2h ago")
        st.markdown(f"**Threats Detected** {len(threats)}")
        st.markdown("**Auto Predicted Mitigations** 12")
        st.markdown("**Model Confidence** 94.2%")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col2:
        st.markdown("**Latest AI Analysis**")
        ai_analysis = st.text_area(
            "AI Analysis", 
            "Detected potential DDoS pattern from subnet 20.0.113.3. Implementing rate limiting and traffic shaping. Confidence: 94.2%",
            height=120
        )
        
        if st.button("🔄 Refresh AI Analysis"):
            st.success("✅ AI analysis refreshed")
    
    # Enhanced Network Activity Chart
    st.markdown("### 📊 Network Activity (24 hours)")
    
    # Generate more realistic data
    hours = list(range(0, 25))
    inbound = [random.randint(20, 160) + int(50 * abs(math.sin(i/4))) for i in hours]
    outbound = [random.randint(15, 140) + int(40 * abs(math.cos(i/3))) for i in hours]
    blocked = [random.randint(5, 30) + int(10 * abs(math.sin(i/2))) for i in hours]
    
    chart_data = pd.DataFrame({
        'Hour': hours,
        'Inbound': inbound,
        'Outbound': outbound,
        'Blocked': blocked
    })
    
    # Create enhanced chart with better styling
    chart = alt.Chart(chart_data).mark_line(strokeWidth=3).encode(
        x=alt.X('Hour:Q', title='Hour of Day'),
        y=alt.Y('value:Q', title='Traffic Volume'),
        color=alt.Color('variable:N', scale=alt.Scale(
            domain=['Inbound', 'Outbound', 'Blocked'],
            range=[SUCCESS_GREEN, TEAL, ERROR_RED]
        ))
    ).transform_fold(
        ['Inbound', 'Outbound', 'Blocked'],
        as_=['variable', 'value']
    ).properties(
        height=300,
        title='Network Traffic Analysis'
    ).configure_axis(
        gridColor='#404040',
        domainColor='#404040',
        labelColor='white',
        titleColor='white'
    ).configure_view(
        strokeWidth=0
    )
    
    st.altair_chart(chart, use_container_width=True)
    
    # Enhanced Recent Threats Table with filtering
    st.markdown("### 🚨 Recent Threats")
    
    # Filter threats based on search
    filtered_threats = threats
    if search_query:
        filtered_threats = [t for t in threats if search_query.lower() in t["type"].lower() or 
                          search_query.lower() in t["description"].lower()]
    
    if filtered_threats:
        threats_df = pd.DataFrame(filtered_threats)
        # Select relevant columns for display
        display_df = threats_df[["id", "type", "severity", "status", "ip", "time", "confidence"]]
        st.dataframe(display_df, use_container_width=True)
    else:
        st.info("No threats found matching your search criteria.")
    
    # Top Bounty Vulnerabilities
    st.markdown("### 💰 Top Bounty Vulnerabilities")
    vulns = generate_vulnerability_data()
    for vuln in vulns[:3]:
        severity_color = {"Critical": "#ff0000", "High": "#ff4444", "Medium": "#ffa500", "Low": "#00ff00"}[vuln["severity"]]
        status_color = {"Open": "#00b8d9", "In Review": "#ffa500", "Fixed": "#00ff00"}[vuln["status"]]
        
        st.markdown(f"""
        <div class="metric-card">
            <h4>{vuln['id']} {vuln['title']}</h4>
            <p><span style="color: {severity_color};">{vuln['severity']}</span> | 
               <span style="color: {status_color};">{vuln['status']}</span></p>
            <p><strong>Bounty:</strong> {vuln['bounty']}</p>
        </div>
        """, unsafe_allow_html=True)

def network_map_page():
    st.markdown('<div class="title-bar">🌐 Network Map</div>', unsafe_allow_html=True)
    
    network_data = generate_network_data()
    
    # Status indicators
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<span class="status-healthy">🟢 Healthy: {network_data["healthy"]}</span>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<span class="status-vulnerable">🟡 Vulnerable: {network_data["vulnerable"]}</span>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<span class="status-compromised">🔴 Compromised: {network_data["compromised"]}</span>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<span style="color: {TEAL};">📊 Total: {network_data["total"]}</span>', unsafe_allow_html=True)
    
    # Network visualization placeholder
    st.markdown("### 🕸️ Network Topology Map")
    st.markdown("Visualize and analyze your network infrastructure")
    
    # Create a simple network graph using plotly
    nodes = []
    edges = []
    
    for i, device in enumerate(network_data["devices"]):
        color = {"healthy": "#00ff00", "vulnerable": "#ffa500", "compromised": "#ff0000"}[device["status"]]
        nodes.append(dict(
            x=[i * 2],
            y=[0],
            mode='markers+text',
            marker=dict(size=30, color=color),
            text=[device["name"]],
            textposition="bottom center",
            name=device["name"]
        ))
    
    fig = go.Figure(data=nodes)
    fig.update_layout(
        title="Network Topology",
        showlegend=False,
        height=400,
        plot_bgcolor=DARK_GRAY,
        paper_bgcolor=DARK_GRAY,
        font=dict(color="white")
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Network Analysis
    st.markdown("### 📈 Network Analysis")
    st.markdown("""
    This network topology map uses a graph-based algorithm to visualize connections. 
    The red highlighted path shows a potential threat vector reaching Server-3, which has identified vulnerabilities.
    
    The system uses BFS (Breadth-First Search) to identify the shortest attack paths and 
    Dijkstra's algorithm to calculate risk propagation metrics across nodes.
    """)

def threat_detection_page():
    st.markdown('<div class="title-bar">🚨 Threat Detection</div>', unsafe_allow_html=True)
    
    # Summary cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Active Threats</h3>
            <h2 style="color: #ff0000;">12</h2>
            <p>Threats detected today</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Auto-Mitigation</h3>
            <h2 style="color: #00ff00;">8</h2>
            <p>Threats automatically mitigated</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>AI Model Accuracy</h3>
            <h2 style="color: #00b8d9;">98.3%</h2>
            <p>Precision in last 1000 predictions</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Active Threats", "Historical Analysis", "Detection Methods", "Performance Metrics"])
    
    with tab1:
        st.markdown("### 🎯 Threat Analysis Dashboard (25)")
        
        threats = generate_threat_data()
        for threat in threats:
            severity_color = {"Critical": "#ff0000", "High": "#ff4444", "Medium": "#ffa500", "Low": "#00ff00"}[threat["severity"]]
            status_color = {"Resolved": "#00ff00", "Unknown": "#ffa500"}[threat["status"]]
            
            col1, col2, col3, col4, col5, col6 = st.columns([2, 1, 1, 1, 1, 2])
            with col1:
                st.markdown(f"**{threat['id']}**")
                st.markdown(f"<span style='color: {severity_color};'>{threat['severity']}</span>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<span style='color: {status_color};'>{threat['status']}</span>", unsafe_allow_html=True)
            with col3:
                st.markdown(f"**{threat['type']}**")
            with col4:
                st.markdown(f"**{threat['ip']}**")
            with col5:
                st.markdown(f"**{threat['time']}**")
            with col6:
                st.markdown(f"**{threat['description']}**")
                st.progress(threat['confidence'] / 100)
                st.markdown(f"AI Confidence: {threat['confidence']}%")
            
            st.markdown("---")

def vulnerability_scanner_page():
    st.markdown('<div class="title-bar">🔍 Vulnerability Scanner</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["New Scan", "Scan History", "Scheduled Scans"])
    
    with tab1:
        st.markdown("### 🆕 New Vulnerability Scan")
        st.markdown("Configure and run a new scan to detect vulnerabilities in your systems.")
        
        # Scan configuration
        with st.expander("🔧 Scan Configuration", expanded=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                scan_target = st.text_input("Target", placeholder="Enter IP address, domain, or CIDR range...", key="scan_target")
            with col2:
                scan_type = st.selectbox("Target Type", ["IP Address", "Domain", "CIDR Range", "URL"], key="scan_type")
            
            # Advanced options
            col1, col2 = st.columns(2)
            with col1:
                port_range = st.text_input("Port Range", value="1-1000", help="Specify port range to scan")
                timeout = st.slider("Timeout (seconds)", 30, 300, 60)
            with col2:
                threads = st.slider("Threads", 1, 50, 10, help="Number of concurrent threads")
                verbosity = st.selectbox("Verbosity", ["Low", "Medium", "High"], index=1)
        
        # Scan type selection
        st.markdown("### 📋 Scan Type")
        scan_options = st.columns(4)
        
        with scan_options[0]:
            quick_scan = st.button("⏱️ Quick Scan", type="primary", use_container_width=True)
            st.markdown("**Fast scan for common vulnerabilities**")
            
        with scan_options[1]:
            full_scan = st.button("🔒 Full Scan", use_container_width=True)
            st.markdown("**Comprehensive security assessment**")
            
        with scan_options[2]:
            web_scan = st.button("🌐 Web App Scan", use_container_width=True)
            st.markdown("**Web application specific vulnerabilities**")
            
        with scan_options[3]:
            custom_scan = st.button("📄 Custom Scan", use_container_width=True)
            st.markdown("**Customized scan parameters**")
        
        # Schedule configuration
        st.markdown("### 📅 Schedule Configuration")
        schedule_cols = st.columns(4)
        
        with schedule_cols[0]:
            run_once = st.button("▶️ Run Once", type="primary", use_container_width=True)
            
        with schedule_cols[1]:
            daily_scan = st.button("📅 Daily", use_container_width=True)
            
        with schedule_cols[2]:
            weekly_scan = st.button("📅 Weekly", use_container_width=True)
            
        with schedule_cols[3]:
            monthly_scan = st.button("📅 Monthly", use_container_width=True)
        
        # File upload for custom scans
        st.markdown("### 📁 Upload Files for Analysis")
        uploaded_file = st.file_uploader(
            "Choose files to scan for vulnerabilities",
            type=['py', 'js', 'php', 'java', 'cpp', 'c', 'html', 'xml', 'json'],
            accept_multiple_files=True,
            help="Upload source code files for static analysis"
        )
        
        if uploaded_file:
            st.success(f"✅ {len(uploaded_file)} file(s) uploaded successfully")
            for file in uploaded_file:
                st.info(f"📄 {file.name} ({file.size} bytes)")
        
        # Action buttons
        st.markdown("### 🚀 Scan Actions")
        action_cols = st.columns([1, 1, 1])
        
        with action_cols[0]:
            if st.button("💾 Save as Template", use_container_width=True):
                st.success("✅ Scan configuration saved as template")
                
        with action_cols[1]:
            if st.button("🔍 Validate Target", use_container_width=True):
                if scan_target:
                    with st.spinner("Validating target..."):
                        # Simulate validation
                        import time
                        time.sleep(1)
                    st.success(f"✅ Target {scan_target} is reachable")
                else:
                    st.error("❌ Please enter a target first")
                    
        with action_cols[2]:
            start_scan = st.button("🚀 Start Scan", type="primary", use_container_width=True)
            
        if start_scan:
            if scan_target:
                st.markdown('<div class="alert-success">🚀 Scan initiated successfully!</div>', unsafe_allow_html=True)
                
                # Progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Simulate scan progress
                for i in range(101):
                    time.sleep(0.05)
                    progress_bar.progress(i)
                    if i < 25:
                        status_text.text(f"🔍 Scanning ports... {i}%")
                    elif i < 50:
                        status_text.text(f"🔍 Checking services... {i}%")
                    elif i < 75:
                        status_text.text(f"🔍 Analyzing vulnerabilities... {i}%")
                    elif i < 100:
                        status_text.text(f"🔍 Generating report... {i}%")
                    else:
                        status_text.text("✅ Scan completed!")
                        
                st.success("🎉 Vulnerability scan completed successfully!")
            else:
                st.error("❌ Please enter a target before starting the scan")

def bug_bounty_page():
    st.markdown('<div class="title-bar">💰 Bug Bounty Program</div>', unsafe_allow_html=True)
    
    # Summary cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Open Issues</h3>
            <h2 style="color: #ff0000;">8</h2>
            <p>Vulnerabilities to address</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Fixed Issues</h3>
            <h2 style="color: #00ff00;">42</h2>
            <p>Vulnerabilities resolved</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Total Rewards</h3>
            <h2 style="color: #00b8d9;">$98,500</h2>
            <p>Bounties awarded to date</p>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Contributors</h3>
            <h2 style="color: #00b8d9;">27</h2>
            <p>Active security researchers</p>
        </div>
        """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Vulnerabilities", "Leaderboard", "Submit Report"])
    
    with tab1:
        st.markdown("### 🗃️ Vulnerability Database")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.text_input("Search vulnerabilities...", placeholder="Enter search term...")
        with col2:
            st.button("➕ Add New")
        
        # Vulnerability table
        vulns = generate_vulnerability_data()
        vuln_df = pd.DataFrame(vulns)
        st.dataframe(vuln_df, use_container_width=True)
        
        # Database structure
        st.markdown("### 🗄️ Database Structure")
        st.markdown("**Vulnerability Tracking Schema**")
        st.markdown("""
        The bug bounty program uses a relational database with four primary tables:
        - `vulnerabilities`: Stores all reported security issues
        - `bounty_submissions`: Tracks researcher submissions and awarded amounts
        - `researchers`: Maintains profiles of participating security researchers
        - `patches`: Documents fix implementations and deployment status
        """)
        
        st.markdown("### 🔐 Access Control Implementation")
        st.markdown("""
        Security researchers are granted granular access based on reputation scores, 
        and an RBAC (Role-Based Access Control) system is implemented with additional 
        constraints based on past performance and submission quality.
        """)

def system_logs_page():
    st.markdown('<div class="title-bar">📋 System Logs</div>', unsafe_allow_html=True)
    
    # Controls
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.selectbox("All Levels", ["All Levels", "ERROR", "WARNING", "INFO", "DEBUG"])
    with col2:
        st.selectbox("Filter", ["All Sources", "Firewall", "Auth Service", "System", "Database"])
    with col3:
        st.button("🔄 Refresh")
    with col4:
        st.button("📤 Export")
    
    # Search
    st.text_input("Search logs...", placeholder="Enter search term...")
    
    # Legend
    st.markdown("🔴 Errors | 🟡 Warnings | 🔵 Info | 🟢 Debug")
    
    # Log table
    logs = generate_log_data()
    log_df = pd.DataFrame(logs)
    st.dataframe(log_df, use_container_width=True)
    
    st.markdown("Showing 9 of 2,461 log entries")
    col1, col2 = st.columns([1, 1])
    with col1:
        st.button("⬅️ Previous")
    with col2:
        st.button("Next ➡️")
    
    # Database schema
    st.markdown("### 🗄️ Database Schema")
    st.markdown("**Log Database Structure**")
    st.markdown("""
    The logging system uses an optimized database schema to store events with minimal 
    overhead while maintaining fast query performance.
    """)
    
    st.code("""
CREATE TABLE system_events (
    event_id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    level VARCHAR(10) NOT NULL,
    source VARCHAR(50) NOT NULL,
    category VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    additional_data JSONB,
    user_id VARCHAR(50),
    ip_address INET,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_timestamp ON system_events(timestamp);
CREATE INDEX idx_level ON system_events(level);
CREATE INDEX idx_source ON system_events(source);
    """, language="sql")
    
    st.markdown("""
    The schema includes indexing strategies and the JSONB field allows for storing 
    additional structured data.
    """)

def settings_page():
    st.markdown('<div class="title-bar">⚙️ System Settings</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["General", "Notifications", "Security", "Database", "Integrations"])
    
    with tab1:
        st.markdown("### 🔧 General Settings")
        st.markdown("Configure general system settings and preferences.")
        
        st.text_input("System Name", value="Cockerel Shield AI Defense")
        st.text_input("Administrator Email", value="admin@example.com")
        
        st.markdown("### 🔄 Automatic Updates")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("Receive system updates automatically")
        with col2:
            st.checkbox("", value=True)
        st.markdown("**Recommended** - System will automatically download and apply security updates.")
        
        st.markdown("### 🤖 AI Defense Module")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("Enable AI-powered threat detection")
        with col2:
            st.checkbox("", value=True, key="ai_enabled")
        st.markdown("Uses machine learning to identify and respond to threats.")
        
        st.markdown("### 📊 Data Retention")
        st.markdown("Retain security logs and events")
        col1, col2 = st.columns([1, 3])
        with col1:
            st.text_input("", value="90")
        with col2:
            st.markdown("days")
        st.markdown("Store security logs and events for the specified period.")
        
        st.button("💾 Save Settings", type="primary")

def security_page():
    st.markdown('<div class="title-bar">🔒 Security Center</div>', unsafe_allow_html=True)
    
    # Security Score
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🛡️ Security Score</h3>
            <h2 style="color: #ffa500;">78/100</h2>
            <p>Your system security score</p>
            <div class="progress-bar" style="width: 78%;"></div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🔐 Authentication Status</h3>
            <p><span style="color: #00ff00;">Strong</span> Password Policy</p>
            <p><span style="color: #ff0000;">Disabled</span> 2FA Status</p>
            <p><span style="color: #ffa500;">Moderate</span> API Key Security</p>
            <p><span style="color: #00ff00;">30 min</span> Session Timeout</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>⚠️ Threat Summary</h3>
            <p><span style="color: #ff0000;">12</span> Active Threats</p>
            <p><span style="color: #ff0000;">8</span> Vulnerabilities</p>
            <p><span style="color: #ff0000;">3</span> <span style="color: #00ff00;">pending</span> Security Patches</p>
            <button>View All Threats</button>
        </div>
        """, unsafe_allow_html=True)
    
    # Security Implementation Details
    st.markdown("### 🔧 Security Implementation Details")
    st.markdown("Technical information about the security modules")
    
    st.markdown("#### 🔐 Cryptography Implementation")
    st.markdown("""
    Industry-standard AES-256 encryption for sensitive data, with RSA-2048 for key exchange. 
    Password hashing is implemented using Argon2id with appropriate memory, iterations, 
    and parallelism parameters to defend against brute force and rainbow table attacks.
    """)
    
    st.markdown("#### 🔑 Authentication System")
    st.markdown("""
    A token-based authentication flow with JWT (JSON Web Tokens) for stateless authentication. 
    Tokens are short-lived (30 minutes) with secure refresh token rotation. The implementation 
    includes protection against CSRF attacks and implements proper CORS policies.
    """)
    
    st.markdown("#### 🚪 Access Control Implementation")
    st.markdown("""
    Role Based Access Control (RBAC) with granular permissions. The access control lists 
    are stored in a secure database and cached for performance. Every API endpoint and 
    UI view has appropriate permission checks, and all access attempts are logged for audit purposes.
    """)

# --- Main Navigation ---
st.sidebar.markdown("## 🛡️ Cockerel Shield")
st.sidebar.markdown("AI Cyber Defense")

# Search in sidebar
st.sidebar.text_input("🔍 Search threats, vulnerabilities, systems...", placeholder="Search...")

st.sidebar.markdown("### Main Navigation")

# Navigation buttons
if st.sidebar.button("📊 Dashboard", use_container_width=True):
    st.session_state.current_page = "Dashboard"
if st.sidebar.button("🌐 Network Map", use_container_width=True):
    st.session_state.current_page = "Network Map"
if st.sidebar.button("🚨 Threat Detection", use_container_width=True):
    st.session_state.current_page = "Threat Detection"
if st.sidebar.button("🔍 Vulnerability Scanner", use_container_width=True):
    st.session_state.current_page = "Vulnerability Scanner"
if st.sidebar.button("💰 Bug Bounty", use_container_width=True):
    st.session_state.current_page = "Bug Bounty"
if st.sidebar.button("📋 System Logs", use_container_width=True):
    st.session_state.current_page = "System Logs"

st.sidebar.markdown("### System")
if st.sidebar.button("⚙️ Settings", use_container_width=True):
    st.session_state.current_page = "Settings"
if st.sidebar.button("🔒 Security", use_container_width=True):
    st.session_state.current_page = "Security"

# System status
st.sidebar.markdown("---")
st.sidebar.markdown("🟢 System operational")

# User info
st.sidebar.markdown("---")
st.sidebar.markdown("👤 Admin User")
st.sidebar.markdown("Security Analyst")

# --- Page Routing ---
if st.session_state.current_page == "Dashboard":
    dashboard_page()
elif st.session_state.current_page == "Network Map":
    network_map_page()
elif st.session_state.current_page == "Threat Detection":
    threat_detection_page()
elif st.session_state.current_page == "Vulnerability Scanner":
    vulnerability_scanner_page()
elif st.session_state.current_page == "Bug Bounty":
    bug_bounty_page()
elif st.session_state.current_page == "System Logs":
    system_logs_page()
elif st.session_state.current_page == "Settings":
    settings_page()
elif st.session_state.current_page == "Security":
    security_page()

# --- Footer ---
st.markdown(f"<hr style='border:1px solid {GRAY};margin-top:40px;margin-bottom:10px;'>", unsafe_allow_html=True)
st.markdown('<div style="text-align:center;color:gray;">&copy; 2024 Cockerel Shield - AI Cyber Defense</div>', unsafe_allow_html=True) 