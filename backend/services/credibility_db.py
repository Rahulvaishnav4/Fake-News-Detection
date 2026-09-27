from typing import Dict, Any, Tuple
from urllib.parse import urlparse
import re

# Comprehensive registry of news domains with credibility tiers and classifications
DOMAIN_REGISTRY: Dict[str, Dict[str, Any]] = {
    # === FACT-CHECKING ORGANIZATIONS (IFCN Certified / Standard Recognized) ===
    "altnews.in": {"tier": "fact_checker", "score": 96, "name": "Alt News", "category": "Fact-Checker"},
    "boomlive.in": {"tier": "fact_checker", "score": 95, "name": "BOOM Live", "category": "Fact-Checker"},
    "snopes.com": {"tier": "fact_checker", "score": 95, "name": "Snopes", "category": "Fact-Checker"},
    "politifact.com": {"tier": "fact_checker", "score": 95, "name": "PolitiFact", "category": "Fact-Checker"},
    "factcheck.org": {"tier": "fact_checker", "score": 95, "name": "FactCheck.org", "category": "Fact-Checker"},
    "fullfact.org": {"tier": "fact_checker", "score": 94, "name": "Full Fact", "category": "Fact-Checker"},
    "vishvasnews.com": {"tier": "fact_checker", "score": 93, "name": "Vishvas News", "category": "Fact-Checker"},
    "newsmobile.in": {"tier": "fact_checker", "score": 92, "name": "NewsMobile Fact Check", "category": "Fact-Checker"},
    "factly.in": {"tier": "fact_checker", "score": 93, "name": "Factly", "category": "Fact-Checker"},
    "pib.gov.in": {"tier": "fact_checker", "score": 95, "name": "PIB Fact Check (Govt of India)", "category": "Official Government"},

    # === TIER 1: AUTHORITATIVE MAINSTREAM & WIRE SERVICES (90-95) ===
    "reuters.com": {"tier": "tier_1", "score": 95, "name": "Reuters", "category": "Global News Wire"},
    "apnews.com": {"tier": "tier_1", "score": 95, "name": "Associated Press (AP)", "category": "Global News Wire"},
    "afp.com": {"tier": "tier_1", "score": 94, "name": "Agence France-Presse (AFP)", "category": "Global News Wire"},
    "bbc.com": {"tier": "tier_1", "score": 93, "name": "BBC News", "category": "Public Broadcaster"},
    "bbc.co.uk": {"tier": "tier_1", "score": 93, "name": "BBC News", "category": "Public Broadcaster"},
    "thehindu.com": {"tier": "tier_1", "score": 93, "name": "The Hindu", "category": "National Newspaper"},
    "indianexpress.com": {"tier": "tier_1", "score": 92, "name": "The Indian Express", "category": "National Newspaper"},
    "timesofindia.indiatimes.com": {"tier": "tier_1", "score": 90, "name": "Times of India", "category": "National Newspaper"},
    "indiatimes.com": {"tier": "tier_1", "score": 89, "name": "IndiaTimes", "category": "Major News Portal"},
    "hindustantimes.com": {"tier": "tier_1", "score": 91, "name": "Hindustan Times", "category": "National Newspaper"},
    "ndtv.com": {"tier": "tier_1", "score": 90, "name": "NDTV", "category": "National News Network"},
    "livemint.com": {"tier": "tier_1", "score": 91, "name": "Mint (Livemint)", "category": "Financial News"},
    "business-standard.com": {"tier": "tier_1", "score": 91, "name": "Business Standard", "category": "Financial News"},
    "economictimes.indiatimes.com": {"tier": "tier_1", "score": 90, "name": "The Economic Times", "category": "Financial News"},
    "bloomberg.com": {"tier": "tier_1", "score": 93, "name": "Bloomberg", "category": "Financial News"},
    "wsj.com": {"tier": "tier_1", "score": 93, "name": "Wall Street Journal", "category": "Financial News"},
    "ft.com": {"tier": "tier_1", "score": 93, "name": "Financial Times", "category": "Financial News"},
    "nytimes.com": {"tier": "tier_1", "score": 92, "name": "The New York Times", "category": "Major Newspaper"},
    "washingtonpost.com": {"tier": "tier_1", "score": 91, "name": "The Washington Post", "category": "Major Newspaper"},
    "theguardian.com": {"tier": "tier_1", "score": 91, "name": "The Guardian", "category": "Major Newspaper"},
    "dw.com": {"tier": "tier_1", "score": 91, "name": "Deutsche Welle (DW)", "category": "Public Broadcaster"},
    "aljazeera.com": {"tier": "tier_1", "score": 89, "name": "Al Jazeera", "category": "International News"},
    "pti.in": {"tier": "tier_1", "score": 94, "name": "Press Trust of India (PTI)", "category": "National News Agency"},
    "aninews.in": {"tier": "tier_1", "score": 89, "name": "Asian News International (ANI)", "category": "News Agency"},
    "nature.com": {"tier": "tier_1", "score": 98, "name": "Nature Journal", "category": "Scientific Journal"},
    "sciencemag.org": {"tier": "tier_1", "score": 98, "name": "Science Journal", "category": "Scientific Journal"},
    "who.int": {"tier": "tier_1", "score": 99, "name": "World Health Organization", "category": "Official Organization"},
    "isro.gov.in": {"tier": "tier_1", "score": 99, "name": "ISRO", "category": "Official Government"},
    "nasa.gov": {"tier": "tier_1", "score": 99, "name": "NASA", "category": "Official Government"},

    # === TIER 2: CREDIBLE SPECIALIZED & REGIONAL MEDIA (78-88) ===
    "thewire.in": {"tier": "tier_2", "score": 85, "name": "The Wire", "category": "Digital Independent"},
    "scroll.in": {"tier": "tier_2", "score": 86, "name": "Scroll.in", "category": "Digital News"},
    "theprint.in": {"tier": "tier_2", "score": 86, "name": "ThePrint", "category": "Digital News"},
    "newslaundry.com": {"tier": "tier_2", "score": 85, "name": "Newslaundry", "category": "Media Watchdog"},
    "indiatoday.in": {"tier": "tier_2", "score": 87, "name": "India Today", "category": "Broadcast & Print"},
    "news18.com": {"tier": "tier_2", "score": 86, "name": "News18", "category": "News Network"},
    "abplive.com": {"tier": "tier_2", "score": 84, "name": "ABP News", "category": "News Network"},
    "deccanherald.com": {"tier": "tier_2", "score": 88, "name": "Deccan Herald", "category": "Regional Newspaper"},
    "dnaindia.com": {"tier": "tier_2", "score": 82, "name": "DNA India", "category": "News Portal"},
    "financialexpress.com": {"tier": "tier_2", "score": 87, "name": "Financial Express", "category": "Financial News"},
    "moneycontrol.com": {"tier": "tier_2", "score": 88, "name": "Moneycontrol", "category": "Financial Media"},
    "forbes.com": {"tier": "tier_2", "score": 86, "name": "Forbes", "category": "Business Media"},
    "techcrunch.com": {"tier": "tier_2", "score": 88, "name": "TechCrunch", "category": "Tech News"},
    "theverge.com": {"tier": "tier_2", "score": 88, "name": "The Verge", "category": "Tech News"},
    "wired.com": {"tier": "tier_2", "score": 88, "name": "Wired", "category": "Tech News"},
    "arstechnica.com": {"tier": "tier_2", "score": 89, "name": "Ars Technica", "category": "Tech News"},
    "espncricinfo.com": {"tier": "tier_2", "score": 90, "name": "ESPN Cricinfo", "category": "Sports Media"},
    "cricbuzz.com": {"tier": "tier_2", "score": 88, "name": "Cricbuzz", "category": "Sports Media"},
    "nationalgeographic.com": {"tier": "tier_2", "score": 90, "name": "National Geographic", "category": "Science Media"},
    "scientificamerican.com": {"tier": "tier_2", "score": 92, "name": "Scientific American", "category": "Science Media"},

    # === SATIRE & PARODY WEBSITES (Known fake for entertainment, score 10-25) ===
    "theonion.com": {"tier": "satire", "score": 15, "name": "The Onion", "category": "Satire / Parody"},
    "babylonbee.com": {"tier": "satire", "score": 15, "name": "The Babylon Bee", "category": "Satire / Parody"},
    "fakingnews.com": {"tier": "satire", "score": 15, "name": "Faking News", "category": "Satire / Parody"},
    "clickhole.com": {"tier": "satire", "score": 15, "name": "ClickHole", "category": "Satire / Parody"},
    "thedailymash.co.uk": {"tier": "satire", "score": 15, "name": "The Daily Mash", "category": "Satire / Parody"},
    "waterfordwhispersnews.com": {"tier": "satire", "score": 15, "name": "Waterford Whispers", "category": "Satire / Parody"},
    "humortimes.com": {"tier": "satire", "score": 15, "name": "Humor Times", "category": "Satire / Parody"},

    # === KNOWN MISINFORMATION / CONSPIRACY / UNVERIFIED LOW-TRUST DOMAINS (score < 40) ===
    "naturalnews.com": {"tier": "unreliable", "score": 25, "name": "Natural News", "category": "Conspiracy / Pseudo-science"},
    "infowars.com": {"tier": "unreliable", "score": 20, "name": "InfoWars", "category": "Conspiracy Media"},
    "beforeitsnews.com": {"tier": "unreliable", "score": 25, "name": "Before It's News", "category": "Unverified User Submissions"},
    "worldnewsdailyreport.com": {"tier": "unreliable", "score": 10, "name": "World News Daily Report", "category": "Hoax / Fake News"},
}

def extract_domain(url_or_domain: str) -> str:
    """Clean and extract normalized root domain from URL or string."""
    if not url_or_domain:
        return ""
    
    clean_str = url_or_domain.strip().lower()
    
    # If it's a full URL, extract hostname
    if clean_str.startswith("http://") or clean_str.startswith("https://"):
        try:
            parsed = urlparse(clean_str)
            clean_str = parsed.hostname or clean_str
        except Exception:
            pass

    # Remove port if any
    clean_str = clean_str.split(":")[0]
    
    # Remove www. and m. prefixes
    clean_str = re.sub(r'^(www\.|m\.)', '', clean_str)
    
    return clean_str

def get_domain_credibility(url_or_source: str) -> Dict[str, Any]:
    """
    Look up credibility metrics for a domain or source name.
    Returns credibility tier, score (0-100), classification name, and trust badge.
    """
    if not url_or_source:
        return {
            "domain": "unknown",
            "name": "Unknown Source",
            "tier": "unverified",
            "score": 50,
            "category": "Unindexed Domain",
            "is_authoritative": False,
            "badge_color": "gray"
        }

    domain = extract_domain(url_or_source)
    
    # Direct match in registry
    if domain in DOMAIN_REGISTRY:
        info = DOMAIN_REGISTRY[domain]
        return {
            "domain": domain,
            "name": info["name"],
            "tier": info["tier"],
            "score": info["score"],
            "category": info["category"],
            "is_authoritative": info["tier"] in ["tier_1", "fact_checker"],
            "badge_color": "green" if info["score"] >= 88 else ("yellow" if info["score"] >= 65 else "red")
        }

    # Suffix match (e.g. subdomains like 'edition.cnn.com' matching 'cnn.com')
    for reg_domain, info in DOMAIN_REGISTRY.items():
        if domain.endswith("." + reg_domain):
            return {
                "domain": domain,
                "name": info["name"],
                "tier": info["tier"],
                "score": info["score"],
                "category": info["category"],
                "is_authoritative": info["tier"] in ["tier_1", "fact_checker"],
                "badge_color": "green" if info["score"] >= 88 else ("yellow" if info["score"] >= 65 else "red")
            }

    # Government or Educational domain heuristics (.gov, .edu, .ac.in, .gov.in)
    if domain.endswith(".gov") or domain.endswith(".gov.in") or domain.endswith(".nic.in"):
        return {
            "domain": domain,
            "name": domain.upper(),
            "tier": "tier_1",
            "score": 96,
            "category": "Official Government Portal",
            "is_authoritative": True,
            "badge_color": "green"
        }
    
    if domain.endswith(".edu") or domain.endswith(".ac.in"):
        return {
            "domain": domain,
            "name": domain,
            "tier": "tier_1",
            "score": 92,
            "category": "Academic / University Research",
            "is_authoritative": True,
            "badge_color": "green"
        }

    # News heuristic keywords
    source_lower = url_or_source.lower()
    if any(k in source_lower for k in ["news", "times", "post", "herald", "chronicle", "tribune", "gazette", "bulletin", "express"]):
        return {
            "domain": domain,
            "name": url_or_source.split("/")[0],
            "tier": "tier_2",
            "score": 75,
            "category": "Recognized News Publisher",
            "is_authoritative": False,
            "badge_color": "blue"
        }

    # Unindexed / General Web Blog / Social Domain
    return {
        "domain": domain,
        "name": domain or url_or_source,
        "tier": "unverified",
        "score": 50,
        "category": "Independent Web Source / Blog",
        "is_authoritative": False,
        "badge_color": "gray"
    }
