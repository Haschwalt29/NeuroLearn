#!/usr/bin/env python3
import subprocess
import sys
import time
import webbrowser
from pathlib import Path


def check_dependencies():
    try:
        import flask  # noqa: F401
        import flask_sqlalchemy  # noqa: F401
        import flask_jwt_extended  # noqa: F401
        import flask_socketio  # noqa: F401
        import deepface  # noqa: F401
        import cv2  # noqa: F401
        import numpy  # noqa: F401
        print("Dependencies OK")
        return True
    except Exception as e:
        print(f"Missing dependency: {e}")
        print("Run: pip install -r requirements.txt")
        return False


def start_backend():
    print("Starting AITutor backend on http://localhost:8002 ...")
    root = Path(__file__).resolve().parents[1]
    return subprocess.Popen([sys.executable, "-m", "aitutor_backend.wsgi"], cwd=root)


def main():
    if not check_dependencies():
        sys.exit(1)
    p = start_backend()
    time.sleep(2)
    webbrowser.open("http://localhost:8002")
    try:
        p.wait()
    except KeyboardInterrupt:
        p.terminate()


if __name__ == "__main__":
    main()


