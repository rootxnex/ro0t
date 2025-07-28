#!/bin/bash

# Cockerel Shield - AI Cyber Defense
# Startup Script

echo "🛡️ Starting Cockerel Shield - AI Cyber Defense"
echo "================================================"

# Check if Python3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python3 is not installed or not in PATH"
    exit 1
fi

# Check if required packages are installed
echo "📦 Checking dependencies..."
python3 -c "import streamlit, fastapi, uvicorn, pandas, altair, plotly, requests" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Error: Required packages are not installed"
    echo "Please run: pip3 install -r requirements.txt"
    exit 1
fi
echo "✅ Dependencies check passed"

# Create data directory if it doesn't exist
mkdir -p data

# Function to cleanup background processes
cleanup() {
    echo "🛑 Shutting down Cockerel Shield..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start Backend API
echo "🚀 Starting Backend API (FastAPI)..."
cd backend
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Check if backend is running
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "❌ Error: Backend API failed to start"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi
echo "✅ Backend API is running on http://localhost:8000"

# Start Frontend (Streamlit)
echo "🚀 Starting Frontend (Streamlit)..."
cd frontend
streamlit run app.py --server.port 8501 --server.address 0.0.0.0 &
FRONTEND_PID=$!
cd ..

# Wait a moment for frontend to start
sleep 5

# Check if frontend is running
if ! curl -s http://localhost:8501 > /dev/null; then
    echo "❌ Error: Frontend failed to start"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 1
fi
echo "✅ Frontend is running on http://localhost:8501"

echo ""
echo "🎉 Cockerel Shield is now running!"
echo "================================================"
echo "🌐 Frontend: http://localhost:8501"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo "================================================"

# Wait for user to stop
wait 