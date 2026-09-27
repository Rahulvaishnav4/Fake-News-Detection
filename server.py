"""
Fake News Detection System - Standalone Standard Server
Runs out of the box using Python's built-in standard library without requiring external pip packages.
"""

import sys
import os
from pathlib import Path
import json
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler

# Add root directory to python path
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

from backend.config import HOST, PORT, FRONTEND_DIR
from backend.services.news_service import get_latest_news, search_google_news
from backend.services.verification_service import verify_news
from backend.database import (
    get_recent_verifications,
    get_verification_by_id,
    get_system_stats,
    save_feedback
)

CATEGORIES = [
    {"id": "all", "label": "Top Stories", "icon": "newspaper"},
    {"id": "india", "label": "India", "icon": "flag"},
    {"id": "world", "label": "World", "icon": "globe"},
    {"id": "technology", "label": "Technology", "icon": "cpu"},
    {"id": "business", "label": "Business", "icon": "briefcase"},
    {"id": "sports", "label": "Sports", "icon": "trophy"},
    {"id": "entertainment", "label": "Entertainment", "icon": "film"},
    {"id": "science", "label": "Science", "icon": "atom"},
    {"id": "politics", "label": "Politics", "icon": "landmark"}
]

class FakeNewsServerHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(FRONTEND_DIR), **kwargs)

    def _send_json(self, data, status_code=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query_params = urllib.parse.parse_qs(parsed.query)

        # Health Check
        if path == "/api/health":
            return self._send_json({"status": "healthy", "service": "Fake News Detection API", "mode": "standalone"})

        # Categories
        if path == "/api/categories":
            return self._send_json({"categories": CATEGORIES})

        # Latest News
        if path == "/api/news/latest":
            cat = query_params.get("category", ["all"])[0]
            try:
                articles = get_latest_news(category=cat)
                return self._send_json({"category": cat, "count": len(articles), "articles": articles})
            except Exception as e:
                return self._send_json({"error": str(e)}, status_code=500)

        # Trending News
        if path == "/api/news/trending":
            try:
                articles = get_latest_news(category="all")
                return self._send_json({"trending": articles[:8] if articles else []})
            except Exception as e:
                return self._send_json({"error": str(e)}, status_code=500)

        # Search News
        if path == "/api/news/search":
            q = query_params.get("q", [""])[0]
            if not q:
                return self._send_json({"error": "Query required"}, status_code=400)
            try:
                results = search_google_news(q)
                return self._send_json({"query": q, "total_results": len(results), "results": results})
            except Exception as e:
                return self._send_json({"error": str(e)}, status_code=500)

        # Verifications History
        if path == "/api/verifications/history":
            try:
                history = get_recent_verifications(limit=15)
                return self._send_json({"history": history})
            except Exception as e:
                return self._send_json({"error": str(e)}, status_code=500)

        # Verification detail by ID: /api/verifications/<id>
        if path.startswith("/api/verifications/"):
            parts = path.split("/")
            if len(parts) >= 4 and parts[3].isdigit():
                v_id = int(parts[3])
                report = get_verification_by_id(v_id)
                if report:
                    return self._send_json(report)
                return self._send_json({"error": "Report not found"}, status_code=404)

        # System Stats
        if path == "/api/stats":
            return self._send_json(get_system_stats())

        # Static files fallback (HTML, CSS, JS)
        if path == "/" or not (FRONTEND_DIR / path.lstrip("/")).exists():
            self.path = "/index.html"
            return super().do_GET()

        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # Read JSON body
        content_len = int(self.headers.get("Content-Length", 0))
        post_body = self.rfile.read(content_len).decode("utf-8")
        try:
            data = json.loads(post_body) if post_body else {}
        except Exception:
            data = {}

        # Verify News
        if path == "/api/verify":
            query = data.get("query", "").strip()
            if not query:
                return self._send_json({"error": "Query is required"}, status_code=400)
            try:
                result = verify_news(query)
                return self._send_json(result)
            except Exception as e:
                return self._send_json({"error": f"Verification error: {str(e)}"}, status_code=500)

        # Submit Feedback
        if path == "/api/feedback":
            v_id = data.get("verification_id")
            helpful = bool(data.get("is_helpful", True))
            comment = data.get("comment", "")
            success = save_feedback(v_id, helpful, comment)
            return self._send_json({"success": success, "message": "Feedback recorded."})

        return self._send_json({"error": "Not Found"}, status_code=404)

def run():
    server_address = (HOST, PORT)
    httpd = HTTPServer(server_address, FakeNewsServerHandler)
    print(f"============================================================")
    print(f"  Fake News Detection System Server")
    print(f"  Running at: http://{HOST}:{PORT}")
    print(f"  Serving UI from: {FRONTEND_DIR}")
    print(f"  API Docs / Endpoints active: /api/news/latest, /api/verify")
    print(f"============================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.server_close()

if __name__ == "__main__":
    run()
