"""News article models."""
from datetime import datetime
from typing import Optional, List
from enum import Enum
from sqlalchemy import String, Text, Integer, Boolean, JSON, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base
from .base import TimestampMixin


class NewsSource(str, Enum):
    """News source enum."""
    TECHCRUNCH = "techcrunch"
    VENTUREBEAT = "venturebeat"
    MIT_TECH_REVIEW = "mit_tech_review"
    GOOGLE_AI = "google_ai"
    OPENAI = "openai"
    DEEPMIND = "deepmind"
    ANTHROPIC = "anthropic"
    HUGGINGFACE = "huggingface"
    TOWARDS_DATA_SCIENCE = "towards_data_science"
    KDNUGGETS = "kdnuggets"
    CUSTOM = "custom"


class NewsArticle(Base, TimestampMixin):
    """News article model."""

    __tablename__ = "news_articles"

    id: Mapped[int] = mapped_column(primary_key=True)
    external_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True)
    source: Mapped[NewsSource] = mapped_column(SQLEnum(NewsSource), nullable=False)

    # Basic Info
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    slug: Mapped[str] = mapped_column(String(550), nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text)
    content: Mapped[Optional[str]] = mapped_column(Text)
    content_html: Mapped[Optional[str]] = mapped_column(Text)

    # Author
    author: Mapped[Optional[str]] = mapped_column(String(255))
    author_url: Mapped[Optional[str]] = mapped_column(String(500))

    # Media
    image_url: Mapped[Optional[str]] = mapped_column(String(500))
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(500))

    # URLs
    url: Mapped[str] = mapped_column(String(500), nullable=False)

    # Categorization
    category: Mapped[Optional[str]] = mapped_column(String(100))
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON)

    # Metrics
    views: Mapped[int] = mapped_column(Integer, default=0)
    shares: Mapped[int] = mapped_column(Integer, default=0)

    # Status
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Dates
    published_at: Mapped[Optional[datetime]] = mapped_column()

    # Extra data
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON)

    def __repr__(self) -> str:
        return f"<NewsArticle {self.title[:50]}...>"
