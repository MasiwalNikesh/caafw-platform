"""Learning resource models."""
from datetime import datetime
from typing import Optional, List
from enum import Enum
from sqlalchemy import String, Text, Integer, Float, Boolean, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base
from .base import TimestampMixin


class ResourceType(str, Enum):
    """Learning resource type enum."""
    COURSE = "course"
    TUTORIAL = "tutorial"
    VIDEO = "video"
    ARTICLE = "article"
    BOOK = "book"
    PODCAST = "podcast"
    WORKSHOP = "workshop"


class LearningResource(Base, TimestampMixin):
    """Learning resource model."""

    __tablename__ = "learning_resources"

    id: Mapped[int] = mapped_column(primary_key=True)
    external_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True)
    source: Mapped[str] = mapped_column(String(50), nullable=False)  # coursera, udemy, youtube, etc.
    resource_type: Mapped[ResourceType] = mapped_column(SQLEnum(ResourceType), nullable=False)

    # Basic Info
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    slug: Mapped[str] = mapped_column(String(550), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Provider
    provider: Mapped[Optional[str]] = mapped_column(String(255))
    instructor: Mapped[Optional[str]] = mapped_column(String(255))
    institution: Mapped[Optional[str]] = mapped_column(String(255))

    # URLs
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    image_url: Mapped[Optional[str]] = mapped_column(String(500))
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(500))

    # Content Info
    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer)
    level: Mapped[Optional[str]] = mapped_column(String(50))  # beginner, intermediate, advanced
    language: Mapped[Optional[str]] = mapped_column(String(50), default="en")

    # Difficulty metadata
    source_difficulty: Mapped[Optional[str]] = mapped_column(String(50))  # Original difficulty from source
    prerequisites: Mapped[Optional[List[str]]] = mapped_column(JSON)  # Required prior knowledge
    is_beginner_friendly: Mapped[bool] = mapped_column(Boolean, default=False)  # Curated beginner content

    # Pricing
    is_free: Mapped[bool] = mapped_column(Boolean, default=False)
    price: Mapped[Optional[float]] = mapped_column(Float)
    currency: Mapped[Optional[str]] = mapped_column(String(10), default="USD")

    # Metrics
    rating: Mapped[Optional[float]] = mapped_column(Float)
    reviews_count: Mapped[int] = mapped_column(Integer, default=0)
    enrollments: Mapped[int] = mapped_column(Integer, default=0)

    # Topics
    topics: Mapped[Optional[List[str]]] = mapped_column(JSON)
    skills: Mapped[Optional[List[str]]] = mapped_column(JSON)

    # Status
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Dates
    published_at: Mapped[Optional[datetime]] = mapped_column()
    last_updated: Mapped[Optional[datetime]] = mapped_column()

    # Extra data
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON)

    # Region (optional - for regional content filtering)
    region_id: Mapped[Optional[int]] = mapped_column(ForeignKey("regions.id", ondelete="SET NULL"))

    def __repr__(self) -> str:
        return f"<LearningResource {self.title[:50]}...>"
