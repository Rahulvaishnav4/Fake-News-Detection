from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="News headline, keyword, or URL to search")
    category: Optional[str] = Field("all", description="Category filter (india, world, technology, etc.)")

class VerifyRequest(BaseModel):
    query: str = Field(..., min_length=2, description="News headline, article snippet, or article URL to verify")

class FeedbackRequest(BaseModel):
    verification_id: Optional[int] = None
    is_helpful: bool
    comment: Optional[str] = ""

class NewsArticle(BaseModel):
    title: str
    source: str
    link: str
    published_at: str
    snippet: str
    category: str
    image_url: str
    credibility: Optional[Dict[str, Any]] = None

class VerificationResult(BaseModel):
    id: Optional[int] = None
    claim: str
    original_query: str
    query_type: str
    status: str
    status_code: str
    confidence: float
    total_sources_found: int
    matching_reliable_sources: int
    tier_1_count: int
    tier_2_count: int
    evidence: Dict[str, List[str]]
    sources: List[Dict[str, Any]]
    linguistic_analysis: Dict[str, Any]
    recommendation: str
    verified_at: str
