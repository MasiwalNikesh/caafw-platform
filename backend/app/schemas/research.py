"""Research paper schemas."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from .common import BaseResponse, PaginatedResponse


class AuthorResponse(BaseResponse):
    """Paper author response schema."""

    id: int
    name: str
    affiliation: Optional[str] = None


class ResearchPaperResponse(BaseResponse):
    """Research paper response schema."""

    id: int
    title: str
    slug: str
    abstract: Optional[str] = None
    source: str
    arxiv_id: Optional[str] = None
    doi: Optional[str] = None
    pdf_url: Optional[str] = None
    paper_url: str
    code_url: Optional[str] = None
    primary_category: Optional[str] = None
    categories: Optional[List[str]] = None
    citations: int = 0
    stars: int = 0
    tasks: Optional[List[str]] = None
    methods: Optional[List[str]] = None
    datasets: Optional[List[str]] = None
    has_code: bool = False
    is_featured: bool = False
    authors: List[AuthorResponse] = []
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class ResearchListResponse(PaginatedResponse[ResearchPaperResponse]):
    """Paginated research paper list response."""

    pass
