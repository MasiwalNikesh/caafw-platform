"""Pydantic schemas for API validation."""
from .common import PaginationParams, PaginatedResponse
from .product import ProductCreate, ProductUpdate, ProductResponse, ProductListResponse
from .job import JobCreate, JobUpdate, JobResponse, JobListResponse
from .news import NewsArticleResponse, NewsListResponse
from .research import ResearchPaperResponse, ResearchListResponse
from .learning import LearningResourceResponse, LearningListResponse
from .mcp_server import MCPServerResponse, MCPServerListResponse
from .community import HackerNewsResponse, RedditPostResponse, GitHubRepoResponse
from .event import EventResponse, EventListResponse
from .investment import CompanyResponse, FundingRoundResponse, CompanyListResponse
from .user import (
    UserCreate, UserLogin, ProfileUpdate,
    UserResponse, UserProfileResponse, UserWithProfileResponse, TokenResponse
)
from .quiz import (
    QuizAnswerSubmit, QuizSubmission,
    QuizQuestionResponse, QuizResultResponse, QuizResultDetailResponse
)
from .admin import (
    # Tags
    TagCreate, TagUpdate, TagResponse, TagListResponse,
    # Categories
    CategoryCreate, CategoryUpdate, CategoryResponse, CategoryTreeResponse,
    # Moderation
    ModerationAction, BulkModerationRequest, ContentModerationResponse,
    # Users
    UserRoleUpdate, UserBanRequest, AdminUserResponse, AdminUserListResponse,
    # API Sources
    APISourceCreate, APISourceUpdate, APISourceResponse, APISourceListResponse,
    APISourceTestRequest, APISourceTestResponse,
    # Audit Log
    AuditLogResponse, AuditLogListResponse,
    # Dashboard
    DashboardStats, DashboardResponse, PendingReviewItem, RecentActivityItem, SourceHealthItem,
    # Content
    AdminContentItem, AdminContentListResponse,
)
from .region import (
    # Regions
    RegionCreate, RegionUpdate, RegionResponse, RegionWithChildrenResponse,
    RegionTreeResponse, RegionListResponse, RegionSimple,
    # Regional Content
    RegionalContentCreate, RegionalContentUpdate, RegionalContentResponse,
    RegionalContentListResponse, RegionalContentBulkCreate, RegionalContentBulkDelete,
    RegionalContentStatusUpdate,
    # API Source with Regions
    APISourceRegionAssignment, APISourceWithRegionsResponse,
)

__all__ = [
    "PaginationParams",
    "PaginatedResponse",
    "ProductCreate",
    "ProductUpdate",
    "ProductResponse",
    "ProductListResponse",
    "JobCreate",
    "JobUpdate",
    "JobResponse",
    "JobListResponse",
    "NewsArticleResponse",
    "NewsListResponse",
    "ResearchPaperResponse",
    "ResearchListResponse",
    "LearningResourceResponse",
    "LearningListResponse",
    "MCPServerResponse",
    "MCPServerListResponse",
    "HackerNewsResponse",
    "RedditPostResponse",
    "GitHubRepoResponse",
    "EventResponse",
    "EventListResponse",
    "CompanyResponse",
    "FundingRoundResponse",
    "CompanyListResponse",
    # User schemas
    "UserCreate",
    "UserLogin",
    "ProfileUpdate",
    "UserResponse",
    "UserProfileResponse",
    "UserWithProfileResponse",
    "TokenResponse",
    # Quiz schemas
    "QuizAnswerSubmit",
    "QuizSubmission",
    "QuizQuestionResponse",
    "QuizResultResponse",
    "QuizResultDetailResponse",
    # Admin schemas - Tags
    "TagCreate",
    "TagUpdate",
    "TagResponse",
    "TagListResponse",
    # Admin schemas - Categories
    "CategoryCreate",
    "CategoryUpdate",
    "CategoryResponse",
    "CategoryTreeResponse",
    # Admin schemas - Moderation
    "ModerationAction",
    "BulkModerationRequest",
    "ContentModerationResponse",
    # Admin schemas - Users
    "UserRoleUpdate",
    "UserBanRequest",
    "AdminUserResponse",
    "AdminUserListResponse",
    # Admin schemas - API Sources
    "APISourceCreate",
    "APISourceUpdate",
    "APISourceResponse",
    "APISourceListResponse",
    "APISourceTestRequest",
    "APISourceTestResponse",
    # Admin schemas - Audit Log
    "AuditLogResponse",
    "AuditLogListResponse",
    # Admin schemas - Dashboard
    "DashboardStats",
    "DashboardResponse",
    "PendingReviewItem",
    "RecentActivityItem",
    "SourceHealthItem",
    # Admin schemas - Content
    "AdminContentItem",
    "AdminContentListResponse",
    # Region schemas
    "RegionCreate",
    "RegionUpdate",
    "RegionResponse",
    "RegionWithChildrenResponse",
    "RegionTreeResponse",
    "RegionListResponse",
    "RegionSimple",
    # Regional Content schemas
    "RegionalContentCreate",
    "RegionalContentUpdate",
    "RegionalContentResponse",
    "RegionalContentListResponse",
    "RegionalContentBulkCreate",
    "RegionalContentBulkDelete",
    "RegionalContentStatusUpdate",
    # API Source with Regions
    "APISourceRegionAssignment",
    "APISourceWithRegionsResponse",
]
