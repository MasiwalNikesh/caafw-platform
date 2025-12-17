"""Product schemas."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, HttpUrl
from .common import BaseResponse, PaginatedResponse


class ProductBase(BaseModel):
    """Base product schema."""

    name: str = Field(..., min_length=1, max_length=255)
    tagline: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    website_url: Optional[str] = None
    pricing_type: Optional[str] = Field(None, pattern="^(free|freemium|paid)$")
    tags: Optional[List[str]] = None


class ProductCreate(ProductBase):
    """Schema for creating a product."""

    slug: str = Field(..., min_length=1, max_length=255)
    source: str = Field(default="manual")
    logo_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    pricing_details: Optional[dict] = None
    category_ids: Optional[List[int]] = None


class ProductUpdate(BaseModel):
    """Schema for updating a product."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    tagline: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    website_url: Optional[str] = None
    logo_url: Optional[str] = None
    pricing_type: Optional[str] = None
    pricing_details: Optional[dict] = None
    tags: Optional[List[str]] = None
    is_featured: Optional[bool] = None
    is_active: Optional[bool] = None


class ProductCategoryResponse(BaseResponse):
    """Product category response schema."""

    id: int
    name: str
    slug: str
    description: Optional[str] = None
    icon: Optional[str] = None


class ProductResponse(BaseResponse):
    """Product response schema."""

    id: int
    name: str
    slug: str
    tagline: Optional[str] = None
    description: Optional[str] = None
    source: str
    website_url: Optional[str] = None
    logo_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    upvotes: int = 0
    comments_count: int = 0
    rating: Optional[float] = None
    reviews_count: int = 0
    pricing_type: Optional[str] = None
    pricing_details: Optional[dict] = None
    is_featured: bool = False
    tags: Optional[List[str]] = None
    categories: List[ProductCategoryResponse] = []
    launched_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class ProductListResponse(PaginatedResponse[ProductResponse]):
    """Paginated product list response."""

    pass
