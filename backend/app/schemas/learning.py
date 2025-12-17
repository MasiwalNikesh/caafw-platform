"""Learning resource schemas."""
from datetime import datetime
from typing import Optional, List
from .common import BaseResponse, PaginatedResponse


class LearningResourceResponse(BaseResponse):
    """Learning resource response schema."""

    id: int
    title: str
    slug: str
    description: Optional[str] = None
    source: str
    resource_type: str
    provider: Optional[str] = None
    instructor: Optional[str] = None
    institution: Optional[str] = None
    url: str
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration_minutes: Optional[int] = None
    level: Optional[str] = None
    language: str = "en"
    is_free: bool = False
    price: Optional[float] = None
    currency: str = "USD"
    rating: Optional[float] = None
    reviews_count: int = 0
    enrollments: int = 0
    topics: Optional[List[str]] = None
    skills: Optional[List[str]] = None
    is_featured: bool = False
    published_at: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class LearningListResponse(PaginatedResponse[LearningResourceResponse]):
    """Paginated learning resource list response."""

    pass
