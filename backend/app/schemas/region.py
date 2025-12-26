"""Region and Regional Content Pydantic schemas for API requests and responses."""
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field
from app.models.region import RegionType
from app.models.regional_content import RegionalContentType
from app.models.admin import ContentStatus


# =============================================================================
# Region Schemas
# =============================================================================

class RegionBase(BaseModel):
    """Base region schema."""
    code: str = Field(..., min_length=1, max_length=20)
    name: str = Field(..., min_length=1, max_length=100)
    region_type: RegionType
    parent_id: Optional[int] = None
    iso_code: Optional[str] = Field(None, max_length=3)
    timezone: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    is_active: bool = True
    sort_order: int = 0


class RegionCreate(RegionBase):
    """Schema for creating a region."""
    pass


class RegionUpdate(BaseModel):
    """Schema for updating a region."""
    code: Optional[str] = Field(None, min_length=1, max_length=20)
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    region_type: Optional[RegionType] = None
    parent_id: Optional[int] = None
    iso_code: Optional[str] = Field(None, max_length=3)
    timezone: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


class RegionResponse(RegionBase):
    """Schema for region response."""
    id: int
    slug: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RegionWithChildrenResponse(RegionResponse):
    """Schema for region response with children."""
    children: List["RegionWithChildrenResponse"] = []

    class Config:
        from_attributes = True


class RegionTreeResponse(BaseModel):
    """Schema for region tree response."""
    regions: List[RegionWithChildrenResponse]


class RegionListResponse(BaseModel):
    """Schema for paginated region list."""
    items: List[RegionResponse]
    total: int


class RegionSimple(BaseModel):
    """Simplified region schema for nested responses."""
    id: int
    code: str
    name: str
    region_type: RegionType
    slug: str

    class Config:
        from_attributes = True


# =============================================================================
# Regional Content Schemas
# =============================================================================

class RegionalContentBase(BaseModel):
    """Base regional content schema."""
    region_id: int
    content_type: RegionalContentType
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    url: Optional[str] = Field(None, max_length=500)
    image_url: Optional[str] = Field(None, max_length=500)
    data: Optional[dict] = None
    is_active: bool = True
    is_featured: bool = False
    sort_order: int = 0


class RegionalContentCreate(RegionalContentBase):
    """Schema for creating regional content."""
    pass


class RegionalContentUpdate(BaseModel):
    """Schema for updating regional content."""
    region_id: Optional[int] = None
    content_type: Optional[RegionalContentType] = None
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    url: Optional[str] = Field(None, max_length=500)
    image_url: Optional[str] = Field(None, max_length=500)
    data: Optional[dict] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None
    sort_order: Optional[int] = None


class RegionalContentResponse(RegionalContentBase):
    """Schema for regional content response."""
    id: int
    slug: str
    region: RegionSimple
    moderation_status: ContentStatus
    created_by_id: Optional[int]
    updated_by_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RegionalContentListResponse(BaseModel):
    """Schema for paginated regional content list."""
    items: List[RegionalContentResponse]
    total: int
    page: int
    page_size: int


class RegionalContentBulkCreate(BaseModel):
    """Schema for bulk creating regional content."""
    items: List[RegionalContentCreate] = Field(..., min_length=1, max_length=100)


class RegionalContentBulkDelete(BaseModel):
    """Schema for bulk deleting regional content."""
    ids: List[int] = Field(..., min_length=1, max_length=100)


class RegionalContentStatusUpdate(BaseModel):
    """Schema for updating regional content status."""
    status: ContentStatus
    reason: Optional[str] = Field(None, max_length=1000)


# =============================================================================
# API Source Region Assignment Schemas
# =============================================================================

class APISourceRegionAssignment(BaseModel):
    """Schema for assigning regions to an API source."""
    region_ids: List[int] = Field(..., min_length=1, max_length=50)


class APISourceWithRegionsResponse(BaseModel):
    """Schema for API source response with regions."""
    id: int
    name: str
    slug: str
    source_type: str
    url: str
    is_active: bool
    requires_api_key: bool
    auto_approve: bool
    fetch_frequency: int
    last_fetched_at: Optional[datetime]
    last_success_at: Optional[datetime]
    last_error: Optional[str]
    error_count: int
    items_fetched: int
    config: Optional[dict]
    regions: List[RegionSimple] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Update forward references
RegionWithChildrenResponse.model_rebuild()
