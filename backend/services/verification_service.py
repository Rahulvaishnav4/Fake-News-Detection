import re
import difflib
from typing import Dict, Any, List, Tuple
from datetime import datetime
from backend.services.news_service import search_google_news, extract_article_from_url, query_google_fact_check
from backend.services.credibility_db import get_domain_credibility, extract_domain
from backend.services.linguistic_analyzer import analyze_linguistics
from backend.database import save_verification

# Common terms that indicate an article is fact-checking or debunking a claim
DEBUNK_KEYWORDS = [
    "fact check", "debunk", "debunked", "false claim", "fake news", "hoax", 
    "misleading", "untrue", "busted", "rumor", "rumour", "fabricated", "doctored"
]

CONFIRM_KEYWORDS = [
    "confirmed", "official", "verified", "announces", "confirms", "statement",
    "accord", "signed", "passed", "won", "wins", "agreed"
]

def clean_search_term(claim: str) -> str:
    """Extract clean keywords from long queries or claims."""
    # Remove excessive punctuation
    clean = re.sub(r'[^\w\s]', ' ', claim)
    words = clean.split()
    # If claim is very long (over 10 words), extract the most significant words
    if len(words) > 10:
        stop_words = {"the", "a", "an", "in", "on", "at", "to", "for", "of", "and", "or", "is", "are", "was", "were", "that", "this", "it", "with", "by", "as"}
        filtered = [w for w in words if w.lower() not in stop_words]
        return " ".join(filtered[:8])
    return " ".join(words)

def compute_similarity(s1: str, s2: str) -> float:
    """Compute token-based and sequence similarity ratio."""
    s1_lower = s1.lower()
    s2_lower = s2.lower()
    
    # Sequence matcher ratio
    seq_ratio = difflib.SequenceMatcher(None, s1_lower, s2_lower).ratio()
    
    # Word set overlap (Jaccard similarity)
    w1 = set(re.findall(r'\b\w{3,}\b', s1_lower))
    w2 = set(re.findall(r'\b\w{3,}\b', s2_lower))
    if not w1 or not w2:
        return seq_ratio
    
    intersection = len(w1.intersection(w2))
    union = len(w1.union(w2))
    jaccard = intersection / union if union > 0 else 0.0
    
    return max(seq_ratio, jaccard)

def verify_news(query_or_url: str) -> Dict[str, Any]:
    """
    Core Multi-Signal Fake News Verification Engine.
    Executes a comprehensive, evidence-grounded assessment:
    1. Determines input type (URL or Headline/Claim)
    2. Searches live Google News / Search sources
    3. Analyzes source domain credibility
    4. Evaluates linguistic style and sensationalism
    5. Searches for active fact-check reports / debunkings
    6. Synthesizes evidence into Likely REAL, Likely FAKE, or UNCERTAIN
    """
    clean_input = query_or_url.strip()
    query_type = "claim"
    extracted_headline = clean_input
    source_url_info = None

    # Step 1: Detect if input is a URL
    if clean_input.startswith("http://") or clean_input.startswith("https://"):
        query_type = "url"
        source_url_info = extract_article_from_url(clean_input)
        extracted_headline = source_url_info.get("title", clean_input)

    # Step 2: Linguistic and Sensationalism Analysis
    linguistic = analyze_linguistics(extracted_headline)

    # Step 3: Search live news sources via Google News RSS
    search_query = clean_search_term(extracted_headline)
    search_results = search_google_news(search_query)

    # Step 4: Fact Check Tool Cross-Reference
    fact_checks = query_google_fact_check(search_query)

    # Step 5: Process and score retrieved sources
    scored_sources = []
    authoritative_sources_count = 0
    tier_1_count = 0
    tier_2_count = 0
    satire_detected = False
    satire_source_name = ""
    debunk_matches = []
    corroborating_sources = []
    total_sources_found = len(search_results)

    # Check origin URL credibility if provided
    if source_url_info:
        origin_cred = source_url_info.get("credibility", {})
        if origin_cred.get("tier") == "satire":
            satire_detected = True
            satire_source_name = origin_cred.get("name", "Satire Portal")

    for article in search_results:
        title = article.get("title", "")
        domain = extract_domain(article.get("link", "") or article.get("source", ""))
        cred = get_domain_credibility(domain)
        
        sim = compute_similarity(extracted_headline, title)
        
        # Check if source is a satire site
        if cred.get("tier") == "satire":
            satire_detected = True
            satire_source_name = cred.get("name", domain)

        # Check for debunking language in retrieved headlines
        is_debunk = any(dbk in title.lower() for dbk in DEBUNK_KEYWORDS)
        if is_debunk:
            debunk_matches.append({
                "source": cred.get("name", domain),
                "headline": title,
                "url": article.get("link", "")
            })

        # Check for positive corroboration
        if sim > 0.35:
            if cred.get("is_authoritative") or cred.get("tier") == "tier_1":
                tier_1_count += 1
                authoritative_sources_count += 1
                corroborating_sources.append(cred.get("name", domain))
            elif cred.get("tier") == "tier_2":
                tier_2_count += 1
                authoritative_sources_count += 1
                corroborating_sources.append(cred.get("name", domain))

        scored_sources.append({
            "title": title,
            "source": cred.get("name", domain),
            "domain": domain,
            "url": article.get("link", ""),
            "published_at": article.get("published_at", ""),
            "snippet": article.get("snippet", ""),
            "credibility_score": cred.get("score", 50),
            "credibility_tier": cred.get("tier", "unverified"),
            "category": cred.get("category", "General"),
            "is_authoritative": cred.get("is_authoritative", False),
            "badge_color": cred.get("badge_color", "gray"),
            "relevance_similarity": round(sim * 100, 1)
        })

    # Sort sources by relevance and credibility
    scored_sources.sort(key=lambda s: (s["relevance_similarity"] * 0.5 + s["credibility_score"] * 0.5), reverse=True)

    # Step 6: Evidence Synthesis
    supporting_evidence: List[str] = []
    warning_signals: List[str] = []
    contradicting_evidence: List[str] = []

    # Linguistic signals
    if linguistic["detected_flags"]:
        for flag in linguistic["detected_flags"]:
            warning_signals.append(f"Linguistic Signal: {flag}")
    if linguistic["positive_indicators"]:
        for ind in linguistic["positive_indicators"]:
            supporting_evidence.append(f"Format: {ind}")

    # Fact checks
    for fc in fact_checks:
        rating = fc.get("rating", "").lower()
        if any(f in rating for f in ["false", "pants on fire", "fake", "incorrect", "misleading"]):
            contradicting_evidence.append(
                f"Fact-Checker ({fc.get('publisher')}): Rated '{fc.get('rating')}' - {fc.get('text')}"
            )
        elif any(t in rating for t in ["true", "correct", "accurate"]):
            supporting_evidence.append(
                f"Fact-Checker ({fc.get('publisher')}): Verified as '{fc.get('rating')}'"
            )

    # Debunk reports in Google News results
    for db in debunk_matches[:3]:
        contradicting_evidence.append(
            f"Debunking headline from {db['source']}: '{db['headline']}'"
        )

    # Corroboration signals
    unique_corroborating = list(set(corroborating_sources))
    if tier_1_count >= 2:
        supporting_evidence.append(
            f"Cross-corroborated by {tier_1_count} authoritative Tier-1 international/national news agencies ({', '.join(unique_corroborating[:4])})"
        )
    elif tier_1_count == 1:
        supporting_evidence.append(
            f"Reported by authoritative news agency: {unique_corroborating[0]}"
        )
    elif tier_2_count >= 2:
        supporting_evidence.append(
            f"Reported by {tier_2_count} mainstream media outlets ({', '.join(unique_corroborating[:3])})"
        )

    if total_sources_found == 0:
        warning_signals.append("No active news reports matching this claim found in current news indexed by Google News.")
    elif authoritative_sources_count == 0 and not debunk_matches:
        warning_signals.append("Claim lacks confirmation from any verified or Tier-1 news organizations.")

    # Step 7: Classification Decision Matrix
    # Status can only be:
    # 🟢 Likely REAL
    # 🔴 Likely FAKE
    # 🟡 UNCERTAIN / NEEDS VERIFICATION

    status = "UNCERTAIN / NEEDS VERIFICATION"
    confidence = 50.0
    recommendation = ""

    # Case A: Satire Portal
    if satire_detected:
        status = "Likely FAKE"
        confidence = 94.0
        contradicting_evidence.append(f"Originated from or attributed to known satire publication '{satire_source_name}' (humor/parody, not real news).")
        recommendation = "This story is from a known parody/satire website. It was written for humor and should not be taken as factual news."

    # Case B: Direct Fact-Check Debunk or Multiple Debunk Headlines
    elif contradicting_evidence and (len(contradicting_evidence) >= 1 or len(debunk_matches) >= 2):
        status = "Likely FAKE"
        confidence = min(96.0, 75.0 + (len(contradicting_evidence) * 7))
        recommendation = "Multiple independent news organizations or fact-checkers have explicitly flagged this claim as false, misleading, or fabricated."

    # Case C: Strong Authoritative Corroboration (Multiple Tier-1)
    elif tier_1_count >= 2 and len(contradicting_evidence) == 0:
        status = "Likely REAL"
        # Confidence increases with more tier-1 sources, penalizing high sensationalism
        confidence = min(96.0, 78.0 + (tier_1_count * 5) - (linguistic["sensationalism_score"] * 0.15))
        recommendation = f"This claim is heavily corroborated by {tier_1_count} major authoritative news agencies with consistent reporting."

    # Case D: Single Tier-1 or Multiple Tier-2 with clean linguistics
    elif (tier_1_count == 1 or tier_2_count >= 2) and linguistic["sensationalism_score"] < 40 and not contradicting_evidence:
        status = "Likely REAL"
        confidence = min(88.0, 70.0 + (authoritative_sources_count * 4))
        recommendation = "Reported by recognized news publishers. Consistent with verified reporting."

    # Case E: High Sensationalism + 0 Authoritative Confirmation
    elif linguistic["sensationalism_score"] > 60 and authoritative_sources_count == 0:
        if total_sources_found == 0:
            status = "Likely FAKE"
            confidence = 76.0
            recommendation = "Contains intense sensationalist/clickbait terminology with zero independent corroboration across Google News. Typical of viral misinformation."
        else:
            status = "UNCERTAIN / NEEDS VERIFICATION"
            confidence = 62.0
            recommendation = "Language is heavily sensationalized, and no mainstream news agencies have confirmed the details. Treat with strong skepticism."

    # Case F: Insufficient Evidence -> Default to UNCERTAIN
    else:
        status = "UNCERTAIN / NEEDS VERIFICATION"
        if authoritative_sources_count == 1:
            confidence = 64.0
            recommendation = "Mentioned in limited sources but lacks broad independent corroboration across major news wires. Wait for official confirmation."
        else:
            confidence = 52.0
            recommendation = "Insufficient verified reporting found online. Automated assessment advises caution until credible news outlets independently verify this claim."

    # Structure full verification result
    result_data = {
        "claim": extracted_headline,
        "original_query": query_or_url,
        "query_type": query_type,
        "status": status,
        "status_code": "real" if "REAL" in status else ("fake" if "FAKE" in status else "uncertain"),
        "confidence": round(confidence, 1),
        "total_sources_found": total_sources_found,
        "matching_reliable_sources": authoritative_sources_count,
        "tier_1_count": tier_1_count,
        "tier_2_count": tier_2_count,
        "evidence": {
            "supporting": supporting_evidence,
            "warnings": warning_signals,
            "contradicting": contradicting_evidence
        },
        "sources": scored_sources[:12],
        "linguistic_analysis": linguistic,
        "recommendation": recommendation,
        "verified_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    }

    # Save to local SQLite database for history and analytics
    verification_id = save_verification(result_data)
    result_data["id"] = verification_id

    return result_data
