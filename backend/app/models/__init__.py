"""Database models for the AI Community Platform."""
from .product import Product, ProductCategory
from .job import Job, JobSource
from .news import NewsArticle, NewsSource
from .research import ResearchPaper, PaperAuthor
from .learning import LearningResource, ResourceType
from .learning_path import LearningPath, UserLearningProgress, PathLevel
from .mcp_server import MCPServer, MCPCategory
from .community import HackerNewsItem, RedditPost, GitHubRepo
from .event import Event, EventType
from .investment import Company, FundingRound
from .user import User, UserProfile, UserLevel
from .quiz import QuizQuestion, QuizResult, QuestionType, QuestionCategory
from .admin import (
    UserRole,
    ContentStatus,
    Tag,
    ContentTag,
    ContentCategory,
    ContentCategoryAssignment,
    AuditLog,
    APISource,
    ContentModeration,
    api_source_regions,
)
from .region import Region, RegionType
from .regional_content import RegionalContent, RegionalContentType
from .bookmark import Bookmark, Collection, CollectionItem, ContentType
from .content_progress import ContentProgress, ProgressStatus

__all__ = [
    # Products
    "Product",
    "ProductCategory",
    # Jobs
    "Job",
    "JobSource",
    # News
    "NewsArticle",
    "NewsSource",
    # Research
    "ResearchPaper",
    "PaperAuthor",
    # Learning
    "LearningResource",
    "ResourceType",
    "LearningPath",
    "UserLearningProgress",
    "PathLevel",
    # MCP
    "MCPServer",
    "MCPCategory",
    # Community
    "HackerNewsItem",
    "RedditPost",
    "GitHubRepo",
    # Events
    "Event",
    "EventType",
    # Investment
    "Company",
    "FundingRound",
    # Users
    "User",
    "UserProfile",
    "UserLevel",
    # Quiz
    "QuizQuestion",
    "QuizResult",
    "QuestionType",
    "QuestionCategory",
    # Admin
    "UserRole",
    "ContentStatus",
    "Tag",
    "ContentTag",
    "ContentCategory",
    "ContentCategoryAssignment",
    "AuditLog",
    "APISource",
    "ContentModeration",
    "api_source_regions",
    # Regions
    "Region",
    "RegionType",
    "RegionalContent",
    "RegionalContentType",
    # Bookmarks
    "Bookmark",
    "Collection",
    "CollectionItem",
    "ContentType",
    # Progress
    "ContentProgress",
    "ProgressStatus",
]
