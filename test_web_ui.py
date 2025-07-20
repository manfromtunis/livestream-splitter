#!/usr/bin/env python3
"""
Test script for Web UI functionality
"""
import os
import sys
import time
import subprocess
import requests
from pathlib import Path

def test_server_startup():
    """Test that the server can start"""
    print("🧪 Testing server startup...")
    
    # Start server in background
    server_process = subprocess.Popen([
        sys.executable, '-m', 'uvicorn', 
        'main:app', '--host', '0.0.0.0', '--port', '8001'
    ], cwd='web/backend', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for server to start
    time.sleep(3)
    
    try:
        # Test if server is running
        response = requests.get('http://localhost:8001')
        if response.status_code == 200:
            print("✅ Server started successfully")
            return True, server_process
        else:
            print(f"❌ Server returned status code: {response.status_code}")
            return False, server_process
    except Exception as e:
        print(f"❌ Could not connect to server: {e}")
        return False, server_process

def test_api_endpoints(base_url='http://localhost:8001'):
    """Test API endpoints"""
    print("🧪 Testing API endpoints...")
    
    tests_passed = 0
    tests_total = 0
    
    # Test root endpoint
    tests_total += 1
    try:
        response = requests.get(f'{base_url}/')
        if response.status_code == 200 and 'Livestream Splitter' in response.text:
            print("✅ Root endpoint works")
            tests_passed += 1
        else:
            print("❌ Root endpoint failed")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
    
    # Test jobs listing
    tests_total += 1
    try:
        response = requests.get(f'{base_url}/api/jobs')
        if response.status_code == 200:
            print("✅ Jobs endpoint works")
            tests_passed += 1
        else:
            print("❌ Jobs endpoint failed")
    except Exception as e:
        print(f"❌ Jobs endpoint error: {e}")
    
    # Test API docs
    tests_total += 1
    try:
        response = requests.get(f'{base_url}/docs')
        if response.status_code == 200:
            print("✅ API documentation available")
            tests_passed += 1
        else:
            print("❌ API documentation failed")
    except Exception as e:
        print(f"❌ API documentation error: {e}")
    
    return tests_passed == tests_total

def test_file_upload_simulation(base_url='http://localhost:8001'):
    """Test file upload endpoint with a small test file"""
    print("🧪 Testing file upload...")
    
    # Create a small test video file
    test_file = Path("test_video.mp4")
    test_file.write_bytes(b"fake video content for testing")
    
    try:
        with open(test_file, 'rb') as f:
            files = {'file': ('test_video.mp4', f, 'video/mp4')}
            response = requests.post(f'{base_url}/api/upload', files=files)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ File upload works: {result}")
            return True
        else:
            print(f"❌ File upload failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ File upload error: {e}")
        return False
    finally:
        # Clean up test file
        if test_file.exists():
            test_file.unlink()

def main():
    """Run all web UI tests"""
    print("🔍 Livestream Splitter - Web UI Test Suite")
    print("=" * 50)
    
    # Ensure we're in virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Not in virtual environment. Activating...")
        activate_script = Path('venv/bin/activate_this.py')
        if activate_script.exists():
            exec(open(activate_script).read(), {'__file__': activate_script})
    
    server_process = None
    all_passed = True
    
    try:
        # Test 1: Server startup
        success, server_process = test_server_startup()
        if not success:
            all_passed = False
            print("⚠️  Server startup failed, skipping other tests")
            return
        
        # Give server a moment to fully initialize
        time.sleep(1)
        
        # Test 2: API endpoints
        if not test_api_endpoints():
            all_passed = False
        
        # Test 3: File upload
        if not test_file_upload_simulation():
            all_passed = False
        
        print("\n" + "=" * 50)
        if all_passed:
            print("🎉 All web UI tests PASSED!")
            print("✅ Web UI is ready for use")
            print("📍 Start with: ./start_web_ui.sh")
        else:
            print("⚠️  Some tests failed")
            
    finally:
        # Clean up server process
        if server_process:
            print("\n🧹 Shutting down test server...")
            server_process.terminate()
            server_process.wait()
    
    return all_passed

if __name__ == "__main__":
    # Install requests if needed
    try:
        import requests
    except ImportError:
        print("Installing requests library...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'requests'])
        import requests
    
    success = main()
    sys.exit(0 if success else 1)