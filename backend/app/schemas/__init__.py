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
]
