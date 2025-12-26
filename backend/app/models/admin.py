"""Admin-related models for content moderation, tags, audit logs, and API sources."""
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from enum import Enum
from sqlalchemy import String, Text, Integer, Boolean, JSON, ForeignKey, Index, Enum as SQLEnum, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import INET
from app.db.database import Base
from .base import TimestampMixin

if TYPE_CHECKING:
    from .user import User
    from .region import Region


# Association table for many-to-many relationship between APISource and Region
api_source_regions = Table(
    "api_source_regions",
    Base.metadata,
    Column("api_source_id", Integer, ForeignKey("api_sources.id", ondelete="CASCADE"), primary_key=True),
    Column("region_id", Integer, ForeignKey("regions.id", ondelete="CASCADE"), primary_key=True),
)


class UserRole(str, Enum):
    """User role enum for access control."""
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class ContentStatus(str, Enum):
    """Content moderation status enum."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    FLAGGED = "flagged"
    ARCHIVED = "archived"


class Tag(Base, TimestampMixin):
    """Tag model for content categorization."""

    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    color: Mapped[Optional[str]] = mapped_column(String(7))  # Hex color like #FF5733
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    content_tags: Mapped[List["ContentTag"]] = relationship(
        back_populates="tag",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Tag {self.name}>"


class ContentTag(Base):
    """Polymorphic association table for content-tag relationships."""

    __tablename__ = "content_tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id", ondelete="CASCADE"), nullable=False)
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'news', 'research', 'job', etc.
    content_id: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relationships
    tag: Mapped["Tag"] = relationship(back_populates="content_tags")

    __table_args__ = (
        Index("idx_content_tags_lookup", "content_type", "content_id"),
        Index("idx_content_tags_unique", "tag_id", "content_type", "content_id", unique=True),
    )

    def __repr__(self) -> str:
        return f"<ContentTag {self.tag_id} -> {self.content_type}:{self.content_id}>"


class ContentCategory(Base, TimestampMixin):
    """Content category model with hierarchical support."""

    __tablename__ = "content_categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("content_categories.id"))
    icon: Mapped[Optional[str]] = mapped_column(String(50))
    color: Mapped[Optional[str]] = mapped_column(String(7))  # Hex color
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    children: Mapped[List["ContentCategory"]] = relationship(
        "ContentCategory",
        backref="parent",
        remote_side=[id],
        cascade="all, delete-orphan",
        single_parent=True
    )
    assignments: Mapped[List["ContentCategoryAssignment"]] = relationship(
        back_populates="category",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<ContentCategory {self.name}>"


class ContentCategoryAssignment(Base):
    """Polymorphic association table for content-category relationships."""

    __tablename__ = "content_category_assignments"

    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("content_categories.id", ondelete="CASCADE"),
        nullable=False
    )
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)
    content_id: Mapped[int] = mapped_column(Integer, nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relationships
    category: Mapped["ContentCategory"] = relationship(back_populates="assignments")

    __table_args__ = (
        Index("idx_category_assignments_lookup", "content_type", "content_id"),
        Index("idx_category_assignments_unique", "category_id", "content_type", "content_id", unique=True),
    )

    def __repr__(self) -> str:
        return f"<ContentCategoryAssignment {self.category_id} -> {self.content_type}:{self.content_id}>"


class AuditLog(Base):
    """Audit log for tracking admin actions."""

    __tablename__ = "admin_audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    admin_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g., 'approve_content', 'ban_user'
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., 'news', 'user', 'job'
    entity_id: Mapped[Optional[int]] = mapped_column(Integer)
    old_values: Mapped[Optional[dict]] = mapped_column(JSON)
    new_values: Mapped[Optional[dict]] = mapped_column(JSON)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))  # IPv6 max length
    user_agent: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, index=True)

    # Relationships
    admin: Mapped["User"] = relationship("User", foreign_keys=[admin_id])

    __table_args__ = (
        Index("idx_audit_log_admin", "admin_id"),
        Index("idx_audit_log_entity", "entity_type", "entity_id"),
    )

    def __repr__(self) -> str:
        return f"<AuditLog {self.action} by {self.admin_id} on {self.entity_type}:{self.entity_id}>"


class APISource(Base, TimestampMixin):
    """Configuration for external API data sources."""

    __tablename__ = "api_sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'rss', 'api', 'scrape'
    url: Mapped[str] = mapped_column(String(500), nullable=False)

    # Configuration
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    requires_api_key: Mapped[bool] = mapped_column(Boolean, default=False)
    auto_approve: Mapped[bool] = mapped_column(Boolean, default=False)  # Trust level
    fetch_frequency: Mapped[int] = mapped_column(Integer, default=360)  # Minutes between fetches

    # Status tracking
    last_fetched_at: Mapped[Optional[datetime]] = mapped_column()
    last_success_at: Mapped[Optional[datetime]] = mapped_column()
    last_error: Mapped[Optional[str]] = mapped_column(Text)
    error_count: Mapped[int] = mapped_column(Integer, default=0)
    items_fetched: Mapped[int] = mapped_column(Integer, default=0)  # Total items fetched

    # Additional configuration as JSON
    config: Mapped[Optional[dict]] = mapped_column(JSON)  # Headers, params, etc.

    # Many-to-many relationship with Region
    regions: Mapped[List["Region"]] = relationship(
        "Region",
        secondary=api_source_regions,
        back_populates="sources"
    )

    def __repr__(self) -> str:
        return f"<APISource {self.name} ({self.source_type})>"


class ContentModeration(Base, TimestampMixin):
    """Track moderation history for content items."""

    __tablename__ = "content_moderation_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)
    content_id: Mapped[int] = mapped_column(Integer, nullable=False)

    # Moderation action
    action: Mapped[str] = mapped_column(String(50), nullable=False)  # 'approve', 'reject', 'flag', 'unflag'
    previous_status: Mapped[Optional[str]] = mapped_column(String(20))
    new_status: Mapped[str] = mapped_column(String(20), nullable=False)

    # Reviewer info
    reviewed_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(Text)  # Reason for rejection/flagging
    notes: Mapped[Optional[str]] = mapped_column(Text)  # Internal notes

    # Relationships
    reviewer: Mapped["User"] = relationship("User", foreign_keys=[reviewed_by])

    __table_args__ = (
        Index("idx_moderation_history_content", "content_type", "content_id"),
        Index("idx_moderation_history_reviewer", "reviewed_by"),
    )

    def __repr__(self) -> str:
        return f"<ContentModeration {self.action} on {self.content_type}:{self.content_id}>"
