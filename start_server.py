#!/usr/bin/env python3
"""
NeuroLearn Backend Startup Script
Handles both development and production environments
"""

import os
import sys
from aitutor_backend import create_app, socketio

def main():
    # Determine environment
    env = os.environ.get('FLASK_ENV', 'development')
    port = int(os.environ.get('PORT', 8002))
    
    # Create app
    app = create_app(config_name=env)
    
    print(f"Starting NeuroLearn Backend in {env} mode on port {port}")
    
    # Run the application
    if env == 'production':
        # Production mode - use eventlet for better performance
        socketio.run(app, host="0.0.0.0", port=port, debug=False)
    else:
        # Development mode - enable debug
        socketio.run(app, host="0.0.0.0", port=port, debug=True)

if __name__ == "__main__":
    main()
