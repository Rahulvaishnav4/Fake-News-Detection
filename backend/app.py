import os
from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path

from backend.config import FRONTEND_DIR, DEBUG
from backend.services.news_service import get_latest_news, search_google_news
from backend.services.verification_service import verify_news
from backend.database import (
    get_recent_searches, 
    get_recent_verifications, 
    get_verification_by_id, 
    get_system_stats, 
    save_feedback
)
from backend.models.schemas import VerifyRequest, FeedbackRequest

app = FastAPI(
    title="Fake News Detection System API",
    description="Automated, evidence-grounded news verification powered by real-time Google News and multi-signal corroboration.",
    version="1.0.0"
)

# CORS Middleware to allow flexible front-end integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Fake News Detection API", "version": "1.0.0"}

@app.get("/api/categories")
def get_categories():
    """Return supported news categories."""
    return {"categories": CATEGORIES}

@app.get("/api/news/latest")
def get_latest(category: str = Query("all", description="Category identifier")):
    """
    Fetch latest real-time news articles from Google News.
    """
    try:
        articles = get_latest_news(category=category)
        return {
            "category": category,
            "count": len(articles),
            "articles": articles
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch latest news: {str(e)}")

@app.get("/api/news/trending")
def get_trending():
    """Fetch top trending headlines from Google News."""
    try:
        articles = get_latest_news(category="all")
        return {
            "trending": articles[:8] if articles else []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch trending news: {str(e)}")

@app.get("/api/news/search")
def search_news(q: str = Query(..., min_length=1, description="Search query")):
    """
    Search live news using Google News search.
    """
    try:
        results = search_google_news(q)
        return {
            "query": q,
            "total_results": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/api/verify")
def verify_claim(req: VerifyRequest):
    """
    Verify a headline, claim, topic, or article URL using multi-signal evidence.
    """
    if not req.query or not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    try:
        result = verify_news(req.query.strip())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verification process failed: {str(e)}")

@app.get("/api/verifications/history")
def verification_history(limit: int = Query(15, ge=1, le=50)):
    """Retrieve history of recently verified news items."""
    try:
        history = get_recent_verifications(limit=limit)
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve history: {str(e)}")

@app.get("/api/verifications/{v_id}")
def verification_detail(v_id: int):
    """Retrieve full verification report by ID."""
    report = get_verification_by_id(v_id)
    if not report:
        raise HTTPException(status_code=404, detail="Verification report not found.")
    return report

@app.get("/api/stats")
def stats():
    """Get system-wide analytics and verification distribution stats."""
    return get_system_stats()

@app.post("/api/feedback")
def submit_feedback(req: FeedbackRequest):
    """Submit user feedback regarding a verification assessment."""
    success = save_feedback(req.verification_id, req.is_helpful, req.comment or "")
    return {"success": success, "message": "Feedback recorded. Thank you!"}

# Serve static frontend files if directory exists
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/")
    def serve_index():
        index_file = FRONTEND_DIR / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return {"message": "Frontend index.html not found"}

    # Catch-all route to serve index.html for SPA client-side routes
    @app.get("/{full_path:path}")
    def catch_all(full_path: str):
        file_path = FRONTEND_DIR / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        index_file = FRONTEND_DIR / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return JSONResponse(status_code=404, content={"message": "Not Found"})
