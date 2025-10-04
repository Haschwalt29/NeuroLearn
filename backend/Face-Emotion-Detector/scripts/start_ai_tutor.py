#!/usr/bin/env python3
"""
AI Tutor Startup Script
Starts both backend and frontend servers
"""

import subprocess
import sys
import time
import webbrowser
import os
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import flask
        import deepface
        import cv2
        import numpy
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def start_backend():
    """Start the Flask backend server"""
    print("🚀 Starting AI Tutor Backend...")
    backend_process = subprocess.Popen([
        sys.executable, "backend/app.py"
    ], cwd=Path(__file__).parent)
    
    # Wait a moment for server to start
    time.sleep(3)
    return backend_process

def start_frontend():
    """Start the frontend development server"""
    print("🎨 Starting AI Tutor Frontend...")
    frontend_dir = Path(__file__).parent / "frontend/ai-tutor"
    
    if not frontend_dir.exists():
        print("❌ Frontend directory not found!")
        return None
    
    frontend_process = subprocess.Popen([
        sys.executable, "-m", "http.server", "8080"
    ], cwd=frontend_dir)
    
    return frontend_process

def main():
    """Main startup function"""
    print("🎓 AI Tutor - Emotion-Adaptive Learning System")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    try:
        # Start backend
        backend_process = start_backend()
        if not backend_process:
            print("❌ Failed to start backend")
            sys.exit(1)
        
        # Start frontend
        frontend_process = start_frontend()
        if not frontend_process:
            print("❌ Failed to start frontend")
            backend_process.terminate()
            sys.exit(1)
        
        print("\n🎉 AI Tutor is now running!")
        print("📱 Frontend: http://localhost:8080")
        print("🔧 Backend API: http://localhost:5000")
        print("\nPress Ctrl+C to stop both servers")
        
        # Open browser
        time.sleep(2)
        webbrowser.open("http://localhost:8080")
        
        # Wait for user to stop
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping AI Tutor...")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    
    finally:
        # Cleanup
        if 'backend_process' in locals():
            backend_process.terminate()
        if 'frontend_process' in locals():
            frontend_process.terminate()
        print("✅ Servers stopped")

if __name__ == "__main__":
    main()
