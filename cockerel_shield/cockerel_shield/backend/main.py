from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
import os
from datetime import datetime
import uuid

app = FastAPI(title="Cockerel Shield API", version="1.0.0")

# Enable CORS for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],  # Streamlit default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class Vulnerability(BaseModel):
    vuln_id: str
    severity: str
    description: str
    cve_id: Optional[str] = None
    affected_component: Optional[str] = None

class ScanRequest(BaseModel):
    filename: str
    file_size: Optional[int] = None

class ScanResponse(BaseModel):
    scan_id: str
    timestamp: str
    filename: str
    vulnerabilities: List[Vulnerability]
    total_vulnerabilities: int

# Mock vulnerability database
MOCK_VULNERABILITIES = [
    {
        "vuln_id": "VULN-001",
        "severity": "High",
        "description": "SQL Injection vulnerability in user authentication module. Attackers can bypass login and gain unauthorized access to sensitive data.",
        "cve_id": "CVE-2024-1234",
        "affected_component": "auth/login.php"
    },
    {
        "vuln_id": "VULN-002", 
        "severity": "Medium",
        "description": "Cross-Site Scripting (XSS) vulnerability in comment system. Malicious scripts can be injected and executed in user browsers.",
        "cve_id": "CVE-2024-5678",
        "affected_component": "comments/display.php"
    },
    {
        "vuln_id": "VULN-003",
        "severity": "Low", 
        "description": "Information disclosure through verbose error messages. System reveals internal file paths and configuration details.",
        "cve_id": "CVE-2024-9012",
        "affected_component": "error_handler.php"
    },
    {
        "vuln_id": "VULN-004",
        "severity": "High",
        "description": "Buffer overflow in file upload handler. Remote code execution possible through crafted file uploads.",
        "cve_id": "CVE-2024-3456",
        "affected_component": "upload/processor.php"
    },
    {
        "vuln_id": "VULN-005",
        "severity": "Medium",
        "description": "Insecure direct object reference (IDOR) in user profile management. Users can access other users' private data.",
        "cve_id": "CVE-2024-7890",
        "affected_component": "profile/view.php"
    }
]

def save_scan_log(scan_data: dict):
    """Save scan results to JSON file"""
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(data_dir, exist_ok=True)
    
    log_file = os.path.join(data_dir, "scan_log.json")
    
    # Load existing logs or create new
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            logs = json.load(f)
    else:
        logs = []
    
    # Add new scan
    logs.append(scan_data)
    
    # Save updated logs
    with open(log_file, 'w') as f:
        json.dump(logs, f, indent=2)

@app.get("/")
async def root():
    return {"message": "Cockerel Shield API is running", "version": "1.0.0"}

@app.post("/scan", response_model=ScanResponse)
async def scan_software(request: ScanRequest):
    """Scan uploaded software for vulnerabilities"""
    try:
        # Generate unique scan ID
        scan_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        # Simulate scanning process (in real app, this would analyze the file)
        # For demo, randomly select 2-3 vulnerabilities
        import random
        num_vulns = random.randint(2, 3)
        selected_vulns = random.sample(MOCK_VULNERABILITIES, num_vulns)
        
        # Convert to Vulnerability objects
        vulnerabilities = [Vulnerability(**vuln) for vuln in selected_vulns]
        
        # Create scan response
        scan_response = ScanResponse(
            scan_id=scan_id,
            timestamp=timestamp,
            filename=request.filename,
            vulnerabilities=vulnerabilities,
            total_vulnerabilities=len(vulnerabilities)
        )
        
        # Save to log file
        save_scan_log(scan_response.dict())
        
        return scan_response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")

@app.get("/scan-history")
async def get_scan_history():
    """Retrieve scan history from log file"""
    try:
        data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
        log_file = os.path.join(data_dir, "scan_log.json")
        
        if not os.path.exists(log_file):
            return {"scans": []}
        
        with open(log_file, 'r') as f:
            logs = json.load(f)
        
        return {"scans": logs}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve scan history: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 