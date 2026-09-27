#!/usr/bin/env python3
"""
Launcher script for Fake News Detection System.
Automatically selects between FastAPI/Uvicorn (if installed) or the built-in standalone server.
"""

import sys
import webbrowser
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from backend.config import HOST, PORT

def open_browser():
    """Wait briefly for server spin-up and launch user browser."""
    time.sleep(1.2)
    url = f"http://{HOST}:{PORT}"
    print(f"Opening browser at: {url}")
    webbrowser.open(url)

def main():
    print("=" * 60)
    print("   Starting Fake News Detection System")
    print(f"   Target URL: http://{HOST}:{PORT}")
    print("=" * 60)

    # Launch browser thread
    import threading
    threading.Thread(target=open_browser, daemon=True).start()

    # Check if uvicorn & fastapi are available
    has_fastapi = False
    try:
        import uvicorn
        import fastapi
        has_fastapi = True
    except ImportError:
        has_fastapi = False

    if has_fastapi:
        print("[Mode] Launching with high-performance FastAPI & Uvicorn engine...")
        try:
            import uvicorn
            uvicorn.run("backend.app:app", host=HOST, port=PORT, reload=True)
            return
        except Exception as e:
            print(f"[Warning] FastAPI launch encountered error: {e}")
            print("[Fallback] Falling back to standard server...")

    # Fallback to standard server
    print("[Mode] Launching with Python Standard Library Server...")
    import server
    server.run()

if __name__ == "__main__":
    main()
