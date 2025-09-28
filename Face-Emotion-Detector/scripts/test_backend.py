#!/usr/bin/env python3
"""
Test script to verify backend is working
"""

import requests
import json

def test_backend():
    """Test the backend API endpoints"""
    base_url = "http://localhost:5000"
    
    print("Testing AI Tutor Backend...")
    print("=" * 40)
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("OK: Backend server is running")
        else:
            print(f"FAIL: Backend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("FAIL: Cannot connect to backend server")
        print("   Make sure to run: python backend/app.py")
        return False
    except Exception as e:
        print(f"FAIL: Error connecting to backend: {e}")
        return False
    
    # Test 2: Test CORS headers
    try:
        response = requests.options(f"{base_url}/upload", timeout=5)
        if "Access-Control-Allow-Origin" in response.headers:
            print("OK: CORS headers are present")
        else:
            print("WARN: CORS headers not found")
    except Exception as e:
        print(f"WARN: CORS test failed: {e}")
    
    # Test 3: Test upload endpoint (without file)
    try:
        response = requests.post(f"{base_url}/upload", timeout=5)
        if response.status_code == 400:
            print("OK: Upload endpoint is responding (expected 400 for no file)")
        else:
            print(f"WARN: Upload endpoint returned unexpected status: {response.status_code}")
    except Exception as e:
        print(f"FAIL: Upload endpoint test failed: {e}")
    
    print("\nBackend tests completed. If all tests passed, try refreshing your browser.")
    return True

if __name__ == "__main__":
    test_backend()
