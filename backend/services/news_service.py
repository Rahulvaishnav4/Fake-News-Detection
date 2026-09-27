import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import re
import json
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
from backend.config import (
    GOOGLE_SEARCH_API_KEY, 
    GOOGLE_SEARCH_ENGINE_ID, 
    GOOGLE_FACT_CHECK_API_KEY,
    NEWS_API_KEY,
    CACHE_TTL_SECONDS
)
from backend.database import cache_news, get_cached_news, log_search
from backend.services.credibility_db import extract_domain, get_domain_credibility

# Map standard category slugs to Google News RSS topic endpoints
GOOGLE_NEWS_CATEGORY_MAP = {
    "all": "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en",
    "india": "https://news.google.com/rss/headlines/section/topic/NATION?hl=en-IN&gl=IN&ceid=IN:en",
    "world": "https://news.google.com/rss/headlines/section/topic/WORLD?hl=en-IN&gl=IN&ceid=IN:en",
    "technology": "https://news.google.com/rss/headlines/section/topic/TECHNOLOGY?hl=en-IN&gl=IN&ceid=IN:en",
    "business": "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=en-IN&gl=IN&ceid=IN:en",
    "sports": "https://news.google.com/rss/headlines/section/topic/SPORTS?hl=en-IN&gl=IN&ceid=IN:en",
    "entertainment": "https://news.google.com/rss/headlines/section/topic/ENTERTAINMENT?hl=en-IN&gl=IN&ceid=IN:en",
    "science": "https://news.google.com/rss/headlines/section/topic/SCIENCE?hl=en-IN&gl=IN&ceid=IN:en",
    "politics": "https://news.google.com/rss/search?q=politics&hl=en-IN&gl=IN&ceid=IN:en"
}

# High quality category fallback imagery
CATEGORY_FALLBACK_IMAGES = {
    "india": "https://images.unsplash.com/photo-1532375810709-75b1da00537c?w=600&auto=format&fit=crop&q=80",
    "world": "https://images.unsplash.com/photo-1526778548025-fa2f459cd5c1?w=600&auto=format&fit=crop&q=80",
    "technology": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=600&auto=format&fit=crop&q=80",
    "business": "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=600&auto=format&fit=crop&q=80",
    "sports": "https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=600&auto=format&fit=crop&q=80",
    "entertainment": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=600&auto=format&fit=crop&q=80",
    "science": "https://images.unsplash.com/photo-1507668077129-56e32842fceb?w=600&auto=format&fit=crop&q=80",
    "politics": "https://images.unsplash.com/photo-1540910419892-4a36d2c3266c?w=600&auto=format&fit=crop&q=80",
    "all": "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=600&auto=format&fit=crop&q=80"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Accept": "application/rss+xml, application/xml, text/xml, */*"
}

def clean_html_tags(raw_html: str) -> str:
    """Remove HTML markup and decode clean text."""
    if not raw_html:
        return ""
    clean = re.sub(r'<[^>]+>', '', raw_html)
    clean = clean.replace('&quot;', '"').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&#39;', "'")
    return clean.strip()

def parse_google_rss_xml(xml_content: str, category: str = "all") -> List[Dict[str, Any]]:
    """Parse Google News RSS XML string into clean structured news items."""
    items: List[Dict[str, Any]] = []
    try:
        root = ET.fromstring(xml_content)
        channel = root.find("channel")
        if channel is None:
            return []

        for item in channel.findall("item"):
            title_el = item.find("title")
            link_el = item.find("link")
            pub_date_el = item.find("pubDate")
            desc_el = item.find("description")
            source_el = item.find("source")

            full_title = title_el.text if title_el is not None and title_el.text else "Untitled News"
            link = link_el.text if link_el is not None and link_el.text else ""
            pub_date = pub_date_el.text if pub_date_el is not None and pub_date_el.text else ""
            raw_desc = desc_el.text if desc_el is not None and desc_el.text else ""

            # Extract source name: Google News titles often end with " - Source Name"
            source_name = "Google News"
            if source_el is not None and source_el.text:
                source_name = source_el.text.strip()
            elif " - " in full_title:
                parts = full_title.rsplit(" - ", 1)
                source_name = parts[1].strip()
                full_title = parts[0].strip()

            clean_snippet = clean_html_tags(raw_desc)
            if clean_snippet.startswith(full_title):
                clean_snippet = clean_snippet[len(full_title):].strip()
            if not clean_snippet:
                clean_snippet = f"Read the full story from {source_name} regarding {full_title}."

            # Image extraction attempt or fallback
            image_url = CATEGORY_FALLBACK_IMAGES.get(category.lower(), CATEGORY_FALLBACK_IMAGES["all"])
            img_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', raw_desc)
            if img_match:
                image_url = img_match.group(1)

            credibility = get_domain_credibility(source_name)

            items.append({
                "title": full_title,
                "source": source_name,
                "link": link,
                "published_at": pub_date,
                "snippet": clean_snippet[:280] + "..." if len(clean_snippet) > 280 else clean_snippet,
                "category": category.capitalize(),
                "image_url": image_url,
                "credibility": credibility
            })

    except Exception as e:
        print(f"Error parsing Google News RSS: {e}")
    return items

def fetch_rss_feed(url: str) -> Optional[str]:
    """Fetch raw XML from Google News RSS using urllib."""
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            return response.read().decode('utf-8', errors='replace')
    except Exception as e:
        print(f"Network error fetching RSS from {url}: {e}")
        return None

def get_latest_news(category: str = "all", use_cache: bool = True) -> List[Dict[str, Any]]:
    """
    Fetch latest real-time news from Google News RSS by category.
    Utilizes local SQLite caching for fast response and reduced requests.
    """
    cat_clean = category.lower().strip()
    
    if use_cache:
        cached = get_cached_news(cat_clean, ttl_seconds=CACHE_TTL_SECONDS)
        if cached and len(cached) >= 4:
            # Augment with credibility info
            for item in cached:
                item["credibility"] = get_domain_credibility(item.get("source", ""))
            return cached

    rss_url = GOOGLE_NEWS_CATEGORY_MAP.get(cat_clean, GOOGLE_NEWS_CATEGORY_MAP["all"])
    xml_data = fetch_rss_feed(rss_url)
    
    if xml_data:
        items = parse_google_rss_xml(xml_data, category=cat_clean)
        if items:
            cache_news(cat_clean, items)
            return items

    # Fallback: if network fails, attempt to read any cached data regardless of TTL
    cached = get_cached_news(cat_clean, ttl_seconds=86400 * 7)
    if cached:
        for item in cached:
            item["credibility"] = get_domain_credibility(item.get("source", ""))
        return cached

    return []

def search_google_news(query: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Search for a news headline, topic, or keyword across Google News RSS.
    Logs search history for analytics and reporting.
    """
    if not query or not query.strip():
        return []

    clean_query = query.strip()
    encoded_query = urllib.parse.quote(clean_query)
    search_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-IN&gl=IN&ceid=IN:en"
    
    xml_data = fetch_rss_feed(search_url)
    results: List[Dict[str, Any]] = []

    if xml_data:
        results = parse_google_rss_xml(xml_data, category=category or "Search")

    # If Google Custom Search API is configured, merge results
    if GOOGLE_SEARCH_API_KEY and GOOGLE_SEARCH_ENGINE_ID:
        try:
            cs_results = search_google_custom_search_api(clean_query)
            if cs_results:
                # Deduplicate by title
                existing_titles = {r["title"].lower() for r in results}
                for csr in cs_results:
                    if csr["title"].lower() not in existing_titles:
                        results.append(csr)
        except Exception as e:
            print(f"Custom Search API query error: {e}")

    log_search(clean_query, search_type="search", results_count=len(results))
    return results

def search_google_custom_search_api(query: str) -> List[Dict[str, Any]]:
    """Query Google Programmable / Custom Search JSON API when configured."""
    if not GOOGLE_SEARCH_API_KEY or not GOOGLE_SEARCH_ENGINE_ID:
        return []

    url = (
        f"https://www.googleapis.com/customsearch/v1?"
        f"key={GOOGLE_SEARCH_API_KEY}&cx={GOOGLE_SEARCH_ENGINE_ID}&q={urllib.parse.quote(query)}"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "FakeNewsDetector/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            items = []
            for item in data.get("items", []):
                domain = extract_domain(item.get("link", ""))
                items.append({
                    "title": item.get("title", ""),
                    "source": domain,
                    "link": item.get("link", ""),
                    "published_at": item.get("snippet", "")[:30],
                    "snippet": item.get("snippet", ""),
                    "category": "Google Search",
                    "image_url": item.get("pagemap", {}).get("cse_image", [{}])[0].get("src", CATEGORY_FALLBACK_IMAGES["all"]),
                    "credibility": get_domain_credibility(domain)
                })
            return items
    except Exception as e:
        print(f"Error querying Google Custom Search API: {e}")
        return []

def query_google_fact_check(query: str) -> List[Dict[str, Any]]:
    """Query Google Fact Check Tools API if configured."""
    if not GOOGLE_FACT_CHECK_API_KEY or not query:
        return []

    url = (
        f"https://factchecktools.googleapis.com/v1alpha1/claims:search?"
        f"query={urllib.parse.quote(query)}&key={GOOGLE_FACT_CHECK_API_KEY}&languageCode=en"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "FakeNewsDetector/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            claims = []
            for c in data.get("claims", []):
                reviews = c.get("claimReview", [])
                for r in reviews:
                    claims.append({
                        "text": c.get("text", ""),
                        "claimant": c.get("claimant", "Unknown"),
                        "publisher": r.get("publisher", {}).get("name", "Fact Checker"),
                        "rating": r.get("textualRating", "Unrated"),
                        "url": r.get("url", "")
                    })
            return claims
    except Exception as e:
        print(f"Google Fact Check API lookup error: {e}")
        return []

def extract_article_from_url(url: str) -> Dict[str, Any]:
    """Extract metadata, title, and body from a news URL."""
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8', errors='replace')
            
            # Simple regex-based metadata extraction
            title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
            og_title = re.search(r'<meta\s+property=["\']og:title["\']\s+content=["\'](.*?)["\']', html, re.IGNORECASE)
            og_desc = re.search(r'<meta\s+property=["\']og:description["\']\s+content=["\'](.*?)["\']', html, re.IGNORECASE)
            og_image = re.search(r'<meta\s+property=["\']og:image["\']\s+content=["\'](.*?)["\']', html, re.IGNORECASE)

            title = og_title.group(1) if og_title else (title_match.group(1) if title_match else url)
            description = og_desc.group(1) if og_desc else ""
            image_url = og_image.group(1) if og_image else CATEGORY_FALLBACK_IMAGES["all"]

            domain = extract_domain(url)
            credibility = get_domain_credibility(domain)

            return {
                "title": clean_html_tags(title),
                "description": clean_html_tags(description),
                "image_url": image_url,
                "url": url,
                "source": domain,
                "credibility": credibility
            }
    except Exception as e:
        print(f"Error fetching URL {url}: {e}")
        domain = extract_domain(url)
        return {
            "title": f"Article from {domain}",
            "description": "Could not access article content directly. Domain will be analyzed.",
            "image_url": CATEGORY_FALLBACK_IMAGES["all"],
            "url": url,
            "source": domain,
            "credibility": get_domain_credibility(domain)
        }
