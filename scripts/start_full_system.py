#!/usr/bin/env python3
"""
Start the complete AI Tutor system
- Backend API server
- Frontend dashboard
- Emotion detection service
"""

import subprocess
import sys
import time
import webbrowser
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import flask
        import flask_sqlalchemy
        import flask_jwt_extended
        import flask_socketio
        import deepface
        import cv2
        import numpy
        print("✅ Backend dependencies OK")
        return True
    except ImportError as e:
        print(f"❌ Missing backend dependency: {e}")
        print("Run: pip install -r requirements.txt")
        return False

def start_backend():
    """Start the Flask backend server"""
    print("🚀 Starting AI Tutor Backend...")
    root = Path(__file__).resolve().parents[1]
    return subprocess.Popen([sys.executable, "-m", "aitutor_backend.wsgi"], cwd=root)

def start_frontend():
    """Start the React frontend development server"""
    print("🎨 Starting AI Tutor Frontend...")
    frontend_dir = Path(__file__).resolve().parents[1] / "frontend" / "dashboard"
    
    if not frontend_dir.exists():
        print("❌ Frontend directory not found!")
        return None
    
    # Install dependencies if needed
    print("📦 Installing frontend dependencies...")
    install_process = subprocess.run(
        ["npm", "install"],
        cwd=frontend_dir,
        capture_output=True,
        text=True
    )
    
    if install_process.returncode != 0:
        print(f"❌ Failed to install frontend dependencies: {install_process.stderr}")
        return None
    
    # Start development server
    frontend_process = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=frontend_dir
    )
    
    return frontend_process

def main():
    """Main startup function"""
    print("🎓 AI Tutor - Complete System Startup")
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
        
        # Wait for backend to start
        print("⏳ Waiting for backend to start...")
        time.sleep(5)
        
        # Start frontend
        frontend_process = start_frontend()
        if not frontend_process:
            print("❌ Failed to start frontend")
            backend_process.terminate()
            sys.exit(1)
        
        print("\n🎉 AI Tutor is now running!")
        print("📱 Frontend Dashboard: http://localhost:3000")
        print("🔧 Backend API: http://localhost:8002")
        print("📊 Emotion Detection: Integrated and ready")
        print("\nPress Ctrl+C to stop both servers")
        
        # Open browser
        time.sleep(3)
        webbrowser.open("http://localhost:3000")
        
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
