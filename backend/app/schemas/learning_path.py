"""Learning path schemas."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from .common import BaseResponse, PaginatedResponse
from .learning import LearningResourceResponse


class LearningPathBase(BaseModel):
    """Base learning path schema."""
    title: str
    slug: str
    description: Optional[str] = None
    level: str
    duration_hours: Optional[int] = None
    topics: Optional[List[str]] = None
    resource_ids: List[int]
    is_featured: bool = False
    is_active: bool = True


class LearningPathCreate(LearningPathBase):
    """Schema for creating a learning path."""
    pass


class LearningPathUpdate(BaseModel):
    """Schema for updating a learning path."""
    title: Optional[str] = None
    description: Optional[str] = None
    level: Optional[str] = None
    duration_hours: Optional[int] = None
    topics: Optional[List[str]] = None
    resource_ids: Optional[List[int]] = None
    is_featured: Optional[bool] = None
    is_active: Optional[bool] = None


class LearningPathResponse(BaseResponse):
    """Learning path response schema."""
    id: int
    title: str
    slug: str
    description: Optional[str] = None
    level: str
    duration_hours: Optional[int] = None
    topics: Optional[List[str]] = None
    resource_ids: List[int]
    is_featured: bool
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    resource_count: int = 0


class LearningPathDetailResponse(LearningPathResponse):
    """Learning path detail response with full resources."""
    resources: List[LearningResourceResponse] = []
    user_progress: Optional["UserProgressResponse"] = None


class UserProgressBase(BaseModel):
    """Base user progress schema."""
    completed_resource_ids: List[int] = []
    current_resource_id: Optional[int] = None
    progress_percentage: int = 0


class UserProgressResponse(BaseResponse):
    """User learning progress response schema."""
    id: int
    user_id: int
    path_id: int
    completed_resource_ids: List[int] = []
    current_resource_id: Optional[int] = None
    progress_percentage: int = 0
    started_at: Optional[datetime] = None
    last_activity_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class UserProgressUpdate(BaseModel):
    """Schema for updating user progress."""
    completed_resource_ids: Optional[List[int]] = None
    current_resource_id: Optional[int] = None


class StartPathResponse(BaseModel):
    """Response when starting a learning path."""
    message: str
    progress: UserProgressResponse


class LearningPathListResponse(PaginatedResponse[LearningPathResponse]):
    """Paginated learning path list response."""
    pass


class PathRecommendation(BaseModel):
    """Path recommendation with reason."""
    path: LearningPathResponse
    reason: str
    match_score: float = Field(ge=0, le=1)


class RecommendationsResponse(BaseModel):
    """Recommendations response."""
    recommendations: List[PathRecommendation]
    user_level: Optional[str] = None


# Forward reference update
LearningPathDetailResponse.model_rebuild()
