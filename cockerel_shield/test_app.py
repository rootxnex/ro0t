#!/usr/bin/env python3
"""
Test script for Cocokerel Shield
Verifies that all components are working correctly
"""

import sys
import requests
import time

def test_backend():
    """Test backend API endpoints"""
    print("🔧 Testing Backend API...")
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
            
        # Test root endpoint
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ Root endpoint working")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
            
        # Test scan endpoint
        scan_data = {
            "filename": "test.php",
            "file_size": 1024
        }
        response = requests.post("http://localhost:8000/scan", json=scan_data, timeout=10)
        if response.status_code == 200:
            print("✅ Scan endpoint working")
        else:
            print(f"❌ Scan endpoint failed: {response.status_code}")
            return False
            
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Backend API is not running")
        return False
    except Exception as e:
        print(f"❌ Backend test failed: {e}")
        return False

def test_frontend():
    """Test frontend accessibility"""
    print("🌐 Testing Frontend...")
    
    try:
        response = requests.get("http://localhost:8501", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is accessible")
            return True
        else:
            print(f"❌ Frontend failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Frontend is not running")
        return False
    except Exception as e:
        print(f"❌ Frontend test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🛡️ Cocokerel Shield - Component Test")
    print("=" * 40)
    
    # Wait a moment for services to start
    print("⏳ Waiting for services to start...")
    time.sleep(3)
    
    backend_ok = test_backend()
    frontend_ok = test_frontend()
    
    print("\n" + "=" * 40)
    if backend_ok and frontend_ok:
        print("🎉 All tests passed! Cocokerel Shield is working correctly.")
        print("\n📊 Access your application:")
        print("   Frontend: http://localhost:8501")
        print("   Backend API: http://localhost:8000")
        print("   API Docs: http://localhost:8000/docs")
    else:
        print("❌ Some tests failed. Please check the logs above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 