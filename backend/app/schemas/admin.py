"""Admin-related Pydantic schemas for API requests and responses."""
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field
from app.models.admin import UserRole, ContentStatus


# =============================================================================
# Tag Schemas
# =============================================================================

class TagBase(BaseModel):
    """Base tag schema."""
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    is_featured: bool = False


class TagCreate(TagBase):
    """Schema for creating a tag."""
    pass


class TagUpdate(BaseModel):
    """Schema for updating a tag."""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = None
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    is_featured: Optional[bool] = None


class TagResponse(TagBase):
    """Schema for tag response."""
    id: int
    slug: str
    usage_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TagListResponse(BaseModel):
    """Schema for paginated tag list."""
    items: List[TagResponse]
    total: int
    page: int
    page_size: int


# =============================================================================
# Category Schemas
# =============================================================================

class CategoryBase(BaseModel):
    """Base category schema."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[int] = None
    icon: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    sort_order: int = 0
    is_active: bool = True


class CategoryCreate(CategoryBase):
    """Schema for creating a category."""
    pass


class CategoryUpdate(BaseModel):
    """Schema for updating a category."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[int] = None
    icon: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class CategoryResponse(CategoryBase):
    """Schema for category response."""
    id: int
    slug: str
    created_at: datetime
    updated_at: datetime
    children: List["CategoryResponse"] = []

    class Config:
        from_attributes = True


class CategoryTreeResponse(BaseModel):
    """Schema for category tree response."""
    categories: List[CategoryResponse]


# =============================================================================
# Content Moderation Schemas
# =============================================================================

class ModerationAction(BaseModel):
    """Schema for moderation action request."""
    reason: Optional[str] = Field(None, max_length=1000)
    notes: Optional[str] = Field(None, max_length=2000)


class BulkModerationRequest(BaseModel):
    """Schema for bulk moderation action."""
    content_type: str = Field(..., pattern=r'^(news|job|product|event|research)$')
    content_ids: List[int] = Field(..., min_length=1, max_length=100)
    action: str = Field(..., pattern=r'^(approve|reject|flag|archive)$')
    reason: Optional[str] = Field(None, max_length=1000)


class ContentModerationResponse(BaseModel):
    """Schema for content moderation history entry."""
    id: int
    content_type: str
    content_id: int
    action: str
    previous_status: Optional[str]
    new_status: str
    reviewed_by: int
    reviewer_name: Optional[str] = None
    reason: Optional[str]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# User Management Schemas
# =============================================================================

class UserRoleUpdate(BaseModel):
    """Schema for updating user role."""
    role: UserRole


class UserBanRequest(BaseModel):
    """Schema for banning a user."""
    reason: str = Field(..., min_length=1, max_length=1000)


class AdminUserResponse(BaseModel):
    """Schema for user response in admin context."""
    id: int
    email: str
    name: Optional[str]
    avatar_url: Optional[str]
    role: UserRole
    is_active: bool
    is_verified: bool
    is_banned: bool
    banned_reason: Optional[str]
    banned_at: Optional[datetime]
    last_login_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AdminUserListResponse(BaseModel):
    """Schema for paginated user list."""
    items: List[AdminUserResponse]
    total: int
    page: int
    page_size: int


# =============================================================================
# API Source Schemas
# =============================================================================

class APISourceBase(BaseModel):
    """Base API source schema."""
    name: str = Field(..., min_length=1, max_length=100)
    source_type: str = Field(..., pattern=r'^(rss|api|scrape)$')
    url: str = Field(..., min_length=1, max_length=500)
    is_active: bool = True
    requires_api_key: bool = False
    auto_approve: bool = False
    fetch_frequency: int = Field(360, ge=5, le=10080)  # 5 min to 1 week
    config: Optional[dict] = None


class APISourceCreate(APISourceBase):
    """Schema for creating an API source."""
    pass


class APISourceUpdate(BaseModel):
    """Schema for updating an API source."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    source_type: Optional[str] = Field(None, pattern=r'^(rss|api|scrape)$')
    url: Optional[str] = Field(None, min_length=1, max_length=500)
    is_active: Optional[bool] = None
    requires_api_key: Optional[bool] = None
    auto_approve: Optional[bool] = None
    fetch_frequency: Optional[int] = Field(None, ge=5, le=10080)
    config: Optional[dict] = None


class APISourceResponse(APISourceBase):
    """Schema for API source response."""
    id: int
    slug: str
    last_fetched_at: Optional[datetime]
    last_success_at: Optional[datetime]
    last_error: Optional[str]
    error_count: int
    items_fetched: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class APISourceListResponse(BaseModel):
    """Schema for API source list."""
    items: List[APISourceResponse]
    total: int


class APISourceTestRequest(BaseModel):
    """Schema for testing an API source."""
    url: str = Field(..., min_length=1, max_length=500)
    source_type: str = Field(..., pattern=r'^(rss|api|scrape)$')
    config: Optional[dict] = None


class APISourceTestResponse(BaseModel):
    """Schema for API source test result."""
    success: bool
    message: str
    sample_items: Optional[List[dict]] = None
    error: Optional[str] = None


# =============================================================================
# Audit Log Schemas
# =============================================================================

class AuditLogResponse(BaseModel):
    """Schema for audit log entry response."""
    id: int
    admin_id: int
    admin_name: Optional[str] = None
    admin_email: Optional[str] = None
    action: str
    entity_type: str
    entity_id: Optional[int]
    old_values: Optional[dict]
    new_values: Optional[dict]
    ip_address: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class AuditLogListResponse(BaseModel):
    """Schema for paginated audit log list."""
    items: List[AuditLogResponse]
    total: int
    page: int
    page_size: int


# =============================================================================
# Dashboard Schemas
# =============================================================================

class PendingReviewStats(BaseModel):
    """Schema for pending review breakdown."""
    news: int = 0
    jobs: int = 0
    products: int = 0
    events: int = 0
    research: int = 0
    total: int = 0


class ContentStats(BaseModel):
    """Schema for content breakdown."""
    news: int = 0
    jobs: int = 0
    products: int = 0
    events: int = 0
    research: int = 0


class APISourceStats(BaseModel):
    """Schema for API source stats."""
    active: int = 0
    with_errors: int = 0


class DashboardStats(BaseModel):
    """Schema for dashboard statistics."""
    pending_review: PendingReviewStats
    total_users: int
    total_content: ContentStats
    api_sources: APISourceStats
    today_approvals: int
    today_rejections: int
    new_users_today: int
    new_users_this_week: int


class PendingReviewItem(BaseModel):
    """Schema for pending review item."""
    id: int
    content_type: str
    title: str
    source: str
    created_at: datetime
    url: Optional[str] = None


class RecentActivityItem(BaseModel):
    """Schema for recent activity item."""
    id: int
    admin_name: str
    action: str
    entity_type: str
    entity_title: Optional[str] = None
    created_at: datetime


class SourceHealthItem(BaseModel):
    """Schema for source health status."""
    id: int
    name: str
    source_type: str
    is_active: bool
    last_fetched_at: Optional[datetime]
    last_error: Optional[str]
    error_count: int
    status: str  # 'ok', 'warning', 'error'


class DashboardResponse(BaseModel):
    """Schema for complete dashboard response."""
    stats: DashboardStats
    pending_review: List[PendingReviewItem]
    recent_activity: List[RecentActivityItem]
    source_health: List[SourceHealthItem]


# =============================================================================
# Content List Schemas (for admin views)
# =============================================================================

class AdminContentItem(BaseModel):
    """Schema for content item in admin list."""
    id: int
    content_type: str
    title: str
    source: str
    moderation_status: ContentStatus
    reviewed_by_name: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    url: Optional[str] = None
    tags: List[str] = []
    categories: List[str] = []

    class Config:
        from_attributes = True


class AdminContentListResponse(BaseModel):
    """Schema for paginated content list in admin."""
    items: List[AdminContentItem]
    total: int
    page: int
    page_size: int
    status_counts: dict  # {'pending': 10, 'approved': 100, ...}


# Update forward references
CategoryResponse.model_rebuild()
