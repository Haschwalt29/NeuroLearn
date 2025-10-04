#!/usr/bin/env python3
"""
Entry point for NeuroLearn backend deployment
Compatible with Render and other cloud platforms
"""

import os
import sys
from pathlib import Path

# Add backend directory to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

try:
    from backend.wsgi import app, socketio
    
    if __name__ == "__main__":
        port = int(os.environ.get("PORT", 8002))
        socketio.run(app, host="0.0.0.0", port=port, debug=False)
        
except ImportError as e:
    print(f"Error importing backend modules: {e}")
    print("Make sure all dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)
