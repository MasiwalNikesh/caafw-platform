"""Regional content model for manually entered region-specific content."""
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from enum import Enum
from sqlalchemy import String, Text, Integer, Boolean, JSON, ForeignKey, Index, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from .base import TimestampMixin
from .admin import ContentStatus

if TYPE_CHECKING:
    from .user import User
    from .region import Region


class RegionalContentType(str, Enum):
    """Content type enum for regional content entries."""
    JOB = "job"
    EVENT = "event"
    NEWS = "news"
    PRODUCT = "product"
    RESEARCH = "research"
    LEARNING = "learning"
    ANNOUNCEMENT = "announcement"
    OTHER = "other"


class RegionalContent(Base, TimestampMixin):
    """Model for manually entered regional content via spreadsheet interface.

    This model allows admins to create region-specific content entries
    that are separate from the auto-collected content from data sources.
    """

    __tablename__ = "regional_content"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Region association
    region_id: Mapped[int] = mapped_column(
        ForeignKey("regions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Content type
    content_type: Mapped[RegionalContentType] = mapped_column(
        SQLEnum(RegionalContentType),
        nullable=False
    )

    # Common content fields
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    slug: Mapped[str] = mapped_column(String(550), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    url: Mapped[Optional[str]] = mapped_column(String(500))
    image_url: Mapped[Optional[str]] = mapped_column(String(500))

    # Flexible data storage for type-specific fields
    # For jobs: company, salary, location, job_type, etc.
    # For events: date, venue, price, etc.
    # For news: author, source, published_date, etc.
    data: Mapped[Optional[dict]] = mapped_column(JSON)

    # Status and visibility
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    moderation_status: Mapped[ContentStatus] = mapped_column(
        SQLEnum(ContentStatus),
        default=ContentStatus.PENDING
    )

    # Display order within region/type
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    # Audit fields
    created_by_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    updated_by_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )

    # Relationships
    region: Mapped["Region"] = relationship("Region")
    created_by: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[created_by_id]
    )
    updated_by: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[updated_by_id]
    )

    __table_args__ = (
        Index("idx_regional_content_region_type", "region_id", "content_type"),
        Index("idx_regional_content_status", "moderation_status"),
        Index("idx_regional_content_active", "is_active"),
        Index("idx_regional_content_featured", "is_featured"),
    )

    def __repr__(self) -> str:
        return f"<RegionalContent {self.id}: {self.title[:50]} ({self.content_type.value})>"
