import sqlite3
import json
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
from backend.config import DB_PATH

def get_db_connection():
    """Create a sqlite3 connection with dict-like row access."""
    # Ensure directory exists
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database tables if they do not exist."""
    conn = get_db_connection()
    try:
        with conn:
            # Search History Table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS search_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    search_type TEXT DEFAULT 'general',
                    results_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Verifications Table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS verifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    claim TEXT NOT NULL,
                    query_type TEXT DEFAULT 'claim',
                    status TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    sources_count INTEGER DEFAULT 0,
                    reliable_sources_count INTEGER DEFAULT 0,
                    evidence_json TEXT,
                    sources_json TEXT,
                    linguistic_json TEXT,
                    recommendation TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Cached News Table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cached_news (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    title TEXT NOT NULL,
                    source TEXT,
                    link TEXT UNIQUE,
                    published_at TEXT,
                    snippet TEXT,
                    image_url TEXT,
                    cached_at INTEGER NOT NULL
                );
            """)

            # User Feedback Table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    verification_id INTEGER,
                    is_helpful INTEGER NOT NULL,
                    comment TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (verification_id) REFERENCES verifications (id)
                );
            """)
    finally:
        conn.close()

# Database helper functions

def log_search(query: str, search_type: str = "general", results_count: int = 0):
    """Log a search query to database."""
    conn = get_db_connection()
    try:
        with conn:
            conn.execute(
                "INSERT INTO search_history (query, search_type, results_count) VALUES (?, ?, ?)",
                (query, search_type, results_count)
            )
    except Exception as e:
        print(f"Error logging search: {e}")
    finally:
        conn.close()

def get_recent_searches(limit: int = 10) -> List[Dict[str, Any]]:
    """Retrieve recent unique searches."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT query, MAX(created_at) as last_searched, COUNT(*) as count 
            FROM search_history 
            GROUP BY query 
            ORDER BY last_searched DESC 
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        print(f"Error fetching searches: {e}")
        return []
    finally:
        conn.close()

def save_verification(data: Dict[str, Any]) -> int:
    """Save a full verification report and return its ID."""
    conn = get_db_connection()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO verifications (
                    claim, query_type, status, confidence, sources_count,
                    reliable_sources_count, evidence_json, sources_json,
                    linguistic_json, recommendation
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data.get("claim", ""),
                data.get("query_type", "claim"),
                data.get("status", "UNCERTAIN / NEEDS VERIFICATION"),
                data.get("confidence", 50.0),
                data.get("sources_count", 0),
                data.get("reliable_sources_count", 0),
                json.dumps(data.get("evidence", {})),
                json.dumps(data.get("sources", [])),
                json.dumps(data.get("linguistic_analysis", {})),
                data.get("recommendation", "")
            ))
            return cursor.lastrowid
    except Exception as e:
        print(f"Error saving verification: {e}")
        return 0
    finally:
        conn.close()

def get_verification_by_id(v_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve a verification by its ID."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM verifications WHERE id = ?", (v_id,))
        row = cursor.fetchone()
        if not row:
            return None
        res = dict(row)
        res["evidence"] = json.loads(res.get("evidence_json") or "{}")
        res["sources"] = json.loads(res.get("sources_json") or "[]")
        res["linguistic_analysis"] = json.loads(res.get("linguistic_json") or "{}")
        return res
    except Exception as e:
        print(f"Error fetching verification {v_id}: {e}")
        return None
    finally:
        conn.close()

def get_recent_verifications(limit: int = 15) -> List[Dict[str, Any]]:
    """Retrieve recent verification checks."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, claim, query_type, status, confidence, 
                   sources_count, reliable_sources_count, created_at 
            FROM verifications 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        print(f"Error fetching verifications history: {e}")
        return []
    finally:
        conn.close()

def get_system_stats() -> Dict[str, Any]:
    """Retrieve aggregate stats for dashboard."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM verifications")
        total_verifications = cursor.fetchone()[0] or 0

        cursor.execute("SELECT status, COUNT(*) FROM verifications GROUP BY status")
        status_counts = {row[0]: row[1] for row in cursor.fetchall()}

        cursor.execute("SELECT COUNT(*) FROM search_history")
        total_searches = cursor.fetchone()[0] or 0

        real_count = status_counts.get("Likely REAL", 0)
        fake_count = status_counts.get("Likely FAKE", 0)
        uncertain_count = status_counts.get("UNCERTAIN / NEEDS VERIFICATION", 0)

        return {
            "total_verifications": total_verifications,
            "total_searches": total_searches,
            "real_count": real_count,
            "fake_count": fake_count,
            "uncertain_count": uncertain_count,
            "real_percentage": round((real_count / total_verifications * 100), 1) if total_verifications else 0,
            "fake_percentage": round((fake_count / total_verifications * 100), 1) if total_verifications else 0,
            "uncertain_percentage": round((uncertain_count / total_verifications * 100), 1) if total_verifications else 0,
        }
    except Exception as e:
        print(f"Error getting stats: {e}")
        return {
            "total_verifications": 0, "total_searches": 0,
            "real_count": 0, "fake_count": 0, "uncertain_count": 0,
            "real_percentage": 0, "fake_percentage": 0, "uncertain_percentage": 0
        }
    finally:
        conn.close()

def cache_news(category: str, items: List[Dict[str, Any]]):
    """Store fetched news articles in cache."""
    now = int(time.time())
    conn = get_db_connection()
    try:
        with conn:
            for item in items:
                conn.execute("""
                    INSERT OR REPLACE INTO cached_news 
                    (category, title, source, link, published_at, snippet, image_url, cached_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    category,
                    item.get("title", ""),
                    item.get("source", "Unknown"),
                    item.get("link", ""),
                    item.get("published_at", ""),
                    item.get("snippet", ""),
                    item.get("image_url", ""),
                    now
                ))
    except Exception as e:
        print(f"Error caching news: {e}")
    finally:
        conn.close()

def get_cached_news(category: str, ttl_seconds: int = 900) -> List[Dict[str, Any]]:
    """Retrieve news articles from cache if not expired."""
    min_cached_at = int(time.time()) - ttl_seconds
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        if category == "all":
            cursor.execute("""
                SELECT category, title, source, link, published_at, snippet, image_url 
                FROM cached_news 
                WHERE cached_at >= ? 
                ORDER BY id DESC 
                LIMIT 50
            """, (min_cached_at,))
        else:
            cursor.execute("""
                SELECT category, title, source, link, published_at, snippet, image_url 
                FROM cached_news 
                WHERE category = ? AND cached_at >= ? 
                ORDER BY id DESC 
                LIMIT 50
            """, (category, min_cached_at))
        return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        print(f"Error reading news cache: {e}")
        return []
    finally:
        conn.close()

def save_feedback(verification_id: Optional[int], is_helpful: bool, comment: str = "") -> bool:
    """Save user feedback."""
    conn = get_db_connection()
    try:
        with conn:
            conn.execute(
                "INSERT INTO feedback (verification_id, is_helpful, comment) VALUES (?, ?, ?)",
                (verification_id, 1 if is_helpful else 0, comment)
            )
            return True
    except Exception as e:
        print(f"Error saving feedback: {e}")
        return False
    finally:
        conn.close()

# Auto-initialize DB on module import
init_db()
