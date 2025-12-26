"""Bookmark and Collection schemas."""
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field
from enum import Enum


class ContentType(str, Enum):
    """Types of content that can be bookmarked."""
    PRODUCT = "product"
    JOB = "job"
    RESEARCH = "research"
    LEARNING = "learning"
    LEARNING_PATH = "learning_path"
    EVENT = "event"
    MCP_SERVER = "mcp_server"
    NEWS = "news"
    HACKERNEWS = "hackernews"
    GITHUB = "github"


# Bookmark schemas
class BookmarkBase(BaseModel):
    content_type: ContentType
    content_id: int
    notes: Optional[str] = None


class BookmarkCreate(BookmarkBase):
    pass


class BookmarkUpdate(BaseModel):
    notes: Optional[str] = None


class BookmarkResponse(BookmarkBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    content_data: Optional[dict] = None  # Populated with actual content details

    class Config:
        from_attributes = True


class BookmarkListResponse(BaseModel):
    items: List[BookmarkResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# Collection schemas
class CollectionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    is_public: bool = False
    color: Optional[str] = None
    icon: Optional[str] = None


class CollectionCreate(CollectionBase):
    pass


class CollectionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_public: Optional[bool] = None
    color: Optional[str] = None
    icon: Optional[str] = None


class CollectionItemResponse(BaseModel):
    id: int
    bookmark_id: int
    order: int
    bookmark: BookmarkResponse

    class Config:
        from_attributes = True


class CollectionResponse(CollectionBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    item_count: int = 0

    class Config:
        from_attributes = True


class CollectionDetailResponse(CollectionResponse):
    items: List[CollectionItemResponse] = []


class CollectionListResponse(BaseModel):
    items: List[CollectionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# Add to collection
class AddToCollectionRequest(BaseModel):
    bookmark_id: int


class ReorderCollectionItemsRequest(BaseModel):
    item_ids: List[int]  # Ordered list of item IDs

