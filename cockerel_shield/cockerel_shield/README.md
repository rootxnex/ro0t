# 🛡️ Cocokerel Shield - Cybersecurity Vulnerability Scanner

A modern cybersecurity application that provides a user-friendly interface for scanning software files for potential vulnerabilities. Built with **Streamlit** for the frontend and **FastAPI** for the backend.

## 🚀 Features

- **File Upload Interface**: Upload various software files for scanning
- **Real-time Vulnerability Scanning**: Instant analysis with mock CVE-style results
- **Interactive Dashboard**: Beautiful UI with vulnerability tables and charts
- **Severity Classification**: High, Medium, and Low severity levels
- **Scan History**: Track and review previous scans
- **Data Persistence**: Store scan results in JSON format
- **Responsive Design**: Modern, professional interface

## 📋 Requirements

- Python 3.8+
- pip (Python package manager)

## 🛠️ Installation

1. **Clone or download the project**:
   ```bash
   # If you have the project files, navigate to the project directory
   cd cockerel_shield
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Running the Application

### Step 1: Start the Backend (FastAPI)

Open a terminal and run:
```bash
cd backend
python main.py
```

The FastAPI server will start on `http://localhost:8000`

### Step 2: Start the Frontend (Streamlit)

Open another terminal and run:
```bash
cd frontend
streamlit run app.py
```

The Streamlit app will open in your browser at `http://localhost:8501`

## 📁 Project Structure

```
cockerel_shield/
├── backend/
│   └── main.py              # FastAPI backend server
├── frontend/
│   └── app.py               # Streamlit frontend application
├── data/
│   └── scan_log.json        # Scan results storage (auto-generated)
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🔧 How to Use

1. **Upload a File**: Use the file uploader to select a software file
2. **Click "Scan Now"**: Initiate the vulnerability scan
3. **View Results**: 
   - Check the vulnerability table for detailed findings
   - Review the severity distribution pie chart
   - Browse scan history for previous results

## 🎯 Supported File Types

- Python (`.py`)
- JavaScript (`.js`)
- PHP (`.php`)
- Java (`.java`)
- C/C++ (`.cpp`, `.c`)
- HTML/CSS (`.html`, `.css`)
- Text files (`.txt`)
- Archives (`.zip`, `.tar`, `.gz`)

## 🔍 Mock Vulnerabilities

The application currently uses mock data to simulate vulnerability scanning. Each scan returns 2-3 randomly selected vulnerabilities from a predefined database including:

- **SQL Injection** vulnerabilities
- **Cross-Site Scripting (XSS)** issues
- **Buffer Overflow** problems
- **Information Disclosure** weaknesses
- **Insecure Direct Object Reference (IDOR)** flaws

## 📊 API Endpoints

### Backend API (FastAPI)

- `GET /` - Health check
- `POST /scan` - Scan uploaded software
- `GET /scan-history` - Retrieve scan history

### Request/Response Format

**Scan Request:**
```json
{
  "filename": "example.py",
  "file_size": 1024
}
```

**Scan Response:**
```json
{
  "scan_id": "uuid-string",
  "timestamp": "2024-01-01T12:00:00",
  "filename": "example.py",
  "vulnerabilities": [
    {
      "vuln_id": "VULN-001",
      "severity": "High",
      "description": "SQL Injection vulnerability...",
      "cve_id": "CVE-2024-1234",
      "affected_component": "auth/login.php"
    }
  ],
  "total_vulnerabilities": 1
}
```

## 🎨 UI Features

- **Modern Dashboard**: Clean, professional interface
- **Color-coded Severity**: Red (High), Orange (Medium), Green (Low)
- **Interactive Charts**: Plotly-powered visualizations
- **Responsive Layout**: Works on different screen sizes
- **Real-time Updates**: Instant feedback on scan progress

## 🔧 Development

### Adding Real Vulnerability Scanning

To integrate real vulnerability scanning:

1. Replace the mock vulnerability generation in `backend/main.py`
2. Implement actual file analysis logic
3. Connect to real CVE databases
4. Add more sophisticated scanning algorithms

### Customizing the UI

- Modify CSS styles in `frontend/app.py`
- Add new visualization components
- Customize the color scheme and layout

## 🐛 Troubleshooting

### Common Issues

1. **Backend Connection Error**:
   - Ensure FastAPI server is running on port 8000
   - Check firewall settings
   - Verify CORS configuration

2. **Port Already in Use**:
   - Change ports in the respective configuration files
   - Kill existing processes using the ports

3. **Dependency Issues**:
   - Update pip: `pip install --upgrade pip`
   - Reinstall requirements: `pip install -r requirements.txt --force-reinstall`

## 📝 License

This is a prototype/demo project for educational purposes.

## 🤝 Contributing

Feel free to enhance this project by:
- Adding real vulnerability scanning capabilities
- Improving the UI/UX
- Adding more file format support
- Implementing authentication
- Adding export functionality

## 📞 Support

For questions or issues, please check the troubleshooting section above or create an issue in the project repository.

---

**Note**: This is a prototype application using mock data. For production use, implement real vulnerability scanning capabilities and security measures. 