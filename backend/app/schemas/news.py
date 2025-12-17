"""News article schemas."""
from datetime import datetime
from typing import Optional, List
from pydantic import Field
from .common import BaseResponse, PaginatedResponse


class NewsArticleResponse(BaseResponse):
    """News article response schema."""

    id: int
    title: str
    slug: str
    summary: Optional[str] = None
    content: Optional[str] = None
    source: str
    author: Optional[str] = None
    author_url: Optional[str] = None
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    url: str
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    views: int = 0
    shares: int = 0
    is_featured: bool = False
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class NewsListResponse(PaginatedResponse[NewsArticleResponse]):
    """Paginated news list response."""

    pass
