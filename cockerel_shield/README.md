# ��️ Cockerel Shield - AI Cyber Defense

A modern, interactive cybersecurity dashboard built with Streamlit and FastAPI, featuring AI-powered threat detection, vulnerability scanning, and comprehensive security monitoring.

## ✨ Features

### 🧠 AI-Powered Security
- **Real-time Threat Detection**: AI models analyze network traffic and system logs
- **Automated Response**: Intelligent mitigation strategies for detected threats
- **Predictive Analytics**: Machine learning models predict potential security risks

### 🔍 Vulnerability Management
- **Multi-format Scanner**: Supports PHP, JavaScript, Python, Java, C++, HTML, XML, JSON
- **File Upload Analysis**: Upload source code files for static analysis
- **CVSS Scoring**: Industry-standard vulnerability severity assessment
- **CVE Integration**: Links to Common Vulnerabilities and Exposures database

### 📊 Interactive Dashboard
- **Real-time Metrics**: Live threat counts, system status, and network activity
- **Interactive Charts**: Beautiful visualizations using Altair and Plotly
- **Search & Filter**: Advanced filtering capabilities for threats and vulnerabilities
- **Responsive Design**: Modern UI with gradient backgrounds and hover effects

### 🌐 Network Monitoring
- **Network Map**: Visual representation of network topology
- **Device Status**: Real-time monitoring of network devices
- **Traffic Analysis**: 24-hour network activity charts
- **Threat Intelligence**: IP reputation and threat correlation

### 💰 Bug Bounty Program
- **Vulnerability Database**: Comprehensive tracking of security issues
- **Bounty Management**: Automated reward calculation and distribution
- **Researcher Portal**: Interface for security researchers
- **Leaderboard**: Competitive ranking system

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip3 package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd cockerel_shield
   ```

2. **Install dependencies**
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Start the application**
   ```bash
   ./start.sh
   ```

4. **Access the application**
   - Frontend: http://localhost:8501
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 🏗️ Architecture

### Frontend (Streamlit)
- **Framework**: Streamlit 1.28.1
- **Charts**: Altair 5.5.0, Plotly 5.17.0
- **Styling**: Custom CSS with gradient themes
- **Data Processing**: Pandas 2.1.3

### Backend (FastAPI)
- **Framework**: FastAPI 0.104.1
- **Server**: Uvicorn 0.24.0
- **Data Models**: Pydantic 2.5.0
- **CORS**: Enabled for frontend communication

### Data Storage
- **Format**: JSON files for scan logs and history
- **Location**: `data/` directory
- **Backup**: Automatic log rotation and archiving

## 🎨 Color Palette

The application uses a professional cybersecurity color scheme:

- **Primary Navy**: `#0A1F44` - Main brand color
- **Electric Teal**: `#00B8D9` - Accent and highlights
- **Success Green**: `#00D4AA` - Positive indicators
- **Warning Orange**: `#FF6B35` - Medium severity alerts
- **Error Red**: `#FF4757` - Critical alerts
- **Info Blue**: `#3742FA` - Information elements
- **Purple**: `#5F27CD` - Special features

## 📱 Pages & Features

### Dashboard
- Real-time threat overview with severity breakdown
- System status monitoring with alert indicators
- AI defense module with confidence scoring
- Interactive network traffic charts
- Searchable threat database

### Vulnerability Scanner
- Multi-format file upload and analysis
- Configurable scan parameters (ports, threads, timeout)
- Scan scheduling (once, daily, weekly, monthly)
- Progress tracking with real-time updates
- Scan history and results storage

### Network Map
- Visual network topology representation
- Device status monitoring (healthy, vulnerable, compromised)
- Network traffic flow visualization
- Device type categorization

### Threat Detection
- Real-time threat monitoring
- Threat type classification
- Confidence scoring for detections
- Historical threat analysis
- Automated response recommendations

### Bug Bounty
- Vulnerability submission and tracking
- Bounty calculation and management
- Researcher leaderboard
- Issue status tracking (Open, In Review, Fixed)

### System Logs
- Comprehensive log monitoring
- Log level filtering (INFO, WARNING, ERROR)
- Source categorization
- Real-time log streaming

## 🔧 Configuration

### Environment Variables
```bash
# Optional: Customize ports
FRONTEND_PORT=8501
BACKEND_PORT=8000

# Optional: Enable debug mode
DEBUG=true
```

### Customization
- **Colors**: Modify color constants in `frontend/app.py`
- **Vulnerabilities**: Update `MOCK_VULNERABILITIES` in `backend/main.py`
- **Charts**: Customize chart configurations in dashboard functions
- **Styling**: Edit CSS in the main app file

## 🧪 Testing

Run the test suite to verify all components:

```bash
python3 test_app.py
```

This will test:
- Backend API endpoints
- Frontend accessibility
- Data generation functions
- Chart rendering

## 📈 Performance

### Optimization Features
- **Lazy Loading**: Charts and data load on demand
- **Caching**: Session state management for better performance
- **Async Operations**: Non-blocking API calls
- **Efficient Rendering**: Optimized chart configurations

### Scalability
- **Modular Design**: Easy to add new features
- **API-First**: Backend can serve multiple frontends
- **Stateless**: Session management for horizontal scaling
- **Data Persistence**: JSON-based storage for easy migration

## 🔒 Security Features

### Built-in Security
- **Input Validation**: Pydantic models for data validation
- **CORS Protection**: Configured for secure cross-origin requests
- **Error Handling**: Graceful error management without information disclosure
- **File Upload Security**: Type and size validation

### Best Practices
- **Principle of Least Privilege**: Minimal required permissions
- **Defense in Depth**: Multiple security layers
- **Secure by Default**: Safe configurations out of the box
- **Regular Updates**: Dependency management for security patches

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at http://localhost:8000/docs
- Review the test suite for usage examples

## 🔮 Roadmap

### Planned Features
- [ ] Real AI model integration
- [ ] Database backend (PostgreSQL)
- [ ] User authentication and authorization
- [ ] Multi-tenant support
- [ ] API rate limiting
- [ ] Webhook integrations
- [ ] Mobile app support
- [ ] Advanced reporting
- [ ] Integration with security tools (Nmap, Metasploit)
- [ ] Compliance reporting (SOC2, ISO27001)

---

**🛡️ Cockerel Shield - Protecting your digital assets with AI-powered cybersecurity** 