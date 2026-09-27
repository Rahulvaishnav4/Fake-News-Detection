import re
from typing import Dict, Any, List

# Patterns frequently present in clickbait or misleading disinformation
CLICKBAIT_PATTERNS = [
    r"\byou won'?t believe\b",
    r"\bshocking (?:truth|revelation|video|facts|photo|moment)\b",
    r"\bwhat happens next\b",
    r"\bdoctors (?:hate|don'?t want you to know)\b",
    r"\bwill blow your mind\b",
    r"\bsecret (?:cure|they don'?t want you to know|formula|agenda)\b",
    r"\bthe truth about\b",
    r"\bmust watch\b",
    r"\bwarning:?\b",
    r"\bshare before (?:it'?s|this gets) deleted\b",
    r"\bviral video reveals\b",
    r"\bunbelievable reason\b",
    r"\bthis is why\b",
    r"\bbreaking:?\s*urgent\b",
    r"\bforward to all\b",
    r"\b100% (?:guaranteed|true|proven)\b",
    r"\bexposed:?\b"
]

# Hyperbolic and emotional trigger words
SENSATIONAL_WORDS = [
    "miracle", "magical", "bizarre", "jaw-dropping", "horrific", "apocalyptic",
    "catastrophic", "pure evil", "disaster", "nightmare", "mind-blowing",
    "unreal", "insane", "bombshell", "treason", "conspiracy", "illuminati",
    "cover-up", "doomsday", "bloodbath", "traitor", "scandalous"
]

# Legitimate journalistic indicator phrases
OBJECTIVE_INDICATORS = [
    r"\baccording to (?:officials|police|ministry|sources|spokesperson|reuters|pti)\b",
    r"\breports suggest\b",
    r"\bannounced on\b",
    r"\bstatement issued by\b",
    r"\bpreliminary findings\b",
    r"\bofficial data\b",
    r"\bgovernment confirmed\b",
    r"\bpress conference\b"
]

def analyze_linguistics(text: str) -> Dict[str, Any]:
    """
    Perform multi-factor linguistic and stylistic evaluation of claim or headline.
    """
    if not text:
        return {
            "sensationalism_score": 0,
            "clickbait_score": 0,
            "overall_linguistic_risk": "Low",
            "detected_flags": [],
            "positive_indicators": [],
            "shouting_detected": False,
            "punctuation_anomaly": False,
            "tone": "Neutral"
        }

    raw_text = text.strip()
    lower_text = raw_text.lower()
    flags: List[str] = []
    positive_indicators: List[str] = []

    # 1. Clickbait regex evaluation
    clickbait_matches = []
    for pattern in CLICKBAIT_PATTERNS:
        match = re.search(pattern, lower_text)
        if match:
            matched_phrase = match.group(0)
            clickbait_matches.append(matched_phrase)
            flags.append(f"Clickbait phrase detected: '{matched_phrase}'")

    # 2. Sensational vocabulary count
    words = re.findall(r'\b[a-zA-Z]+\b', lower_text)
    total_words = max(len(words), 1)
    sensational_found = [w for w in words if w in SENSATIONAL_WORDS]
    if sensational_found:
        unique_sensational = list(set(sensational_found))
        flags.append(f"Sensationalist terminology: {', '.join(unique_sensational)}")

    # 3. Capitalization / Shouting test
    uppercase_chars = sum(1 for c in raw_text if c.isupper())
    alpha_chars = sum(1 for c in raw_text if c.isalpha())
    caps_ratio = (uppercase_chars / alpha_chars) if alpha_chars > 0 else 0
    shouting = False
    if caps_ratio > 0.45 and len(raw_text) > 15:
        shouting = True
        flags.append(f"Excessive capitalization ({round(caps_ratio * 100)}% uppercase) indicating sensationalist shouting")

    # 4. Punctuation anomalies (multiple exclamation or question marks)
    punctuation_anomaly = False
    if re.search(r'[!?]{2,}', raw_text):
        punctuation_anomaly = True
        flags.append("Repeated exclamation or question marks (e.g., '!!', '??', '?!')")

    # 5. Objective / Journalistic indicators check
    for pattern in OBJECTIVE_INDICATORS:
        if re.search(pattern, lower_text):
            positive_indicators.append("Contains attribution to formal authority/reporting institution")
            break

    # Calculate scores
    clickbait_score = min(100, len(clickbait_matches) * 35 + (20 if punctuation_anomaly else 0))
    sensationalism_score = min(100, int((len(sensational_found) / max(total_words, 5)) * 250) + (25 if shouting else 0))

    combined_risk = (clickbait_score * 0.6) + (sensationalism_score * 0.4)
    
    if combined_risk > 60:
        tone = "High Clickbait / Sensationalist"
        risk_level = "High"
    elif combined_risk > 25:
        tone = "Mild Sensationalism / Emotionally Charged"
        risk_level = "Moderate"
    else:
        tone = "Objective / Journalistic"
        risk_level = "Low"

    return {
        "sensationalism_score": sensationalism_score,
        "clickbait_score": clickbait_score,
        "overall_linguistic_risk": risk_level,
        "detected_flags": flags,
        "positive_indicators": positive_indicators,
        "shouting_detected": shouting,
        "punctuation_anomaly": punctuation_anomaly,
        "tone": tone
    }
