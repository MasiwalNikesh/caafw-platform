"""Bookmark and Collection models for user content curation."""
from datetime import datetime
from enum import Enum
from typing import Optional, List
from sqlalchemy import (
    String,
    Integer,
    Text,
    Boolean,
    ForeignKey,
    DateTime,
    UniqueConstraint,
    Index,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from app.models.base import TimestampMixin


class ContentType(str, Enum):
    """Types of content that can be bookmarked."""
    PRODUCT = "product"
    JOB = "job"
    RESEARCH = "research"
    LEARNING = "learning"
    LEARNING_PATH = "learning_path"
    EVENT = "event"
    MCP_SERVER = "mcp_server"
    NEWS = "news"
    HACKERNEWS = "hackernews"
    GITHUB = "github"


class Bookmark(Base, TimestampMixin):
    """User bookmarks for any content type."""
    
    __tablename__ = "bookmarks"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    content_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    content_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="bookmarks")
    collection_items = relationship(
        "CollectionItem",
        back_populates="bookmark",
        cascade="all, delete-orphan",
    )
    
    __table_args__ = (
        UniqueConstraint("user_id", "content_type", "content_id", name="unique_user_bookmark"),
        Index("idx_bookmark_content", "content_type", "content_id"),
    )


class Collection(Base, TimestampMixin):
    """User-created collections to organize bookmarks."""
    
    __tablename__ = "collections"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    color: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # For UI customization
    icon: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # Icon name
    
    # Relationships
    user = relationship("User", back_populates="collections")
    items = relationship(
        "CollectionItem",
        back_populates="collection",
        cascade="all, delete-orphan",
        order_by="CollectionItem.order",
    )
    
    __table_args__ = (
        Index("idx_collection_user", "user_id"),
    )


class CollectionItem(Base, TimestampMixin):
    """Items within a collection (references bookmarks)."""
    
    __tablename__ = "collection_items"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    collection_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("collections.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    bookmark_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("bookmarks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Relationships
    collection = relationship("Collection", back_populates="items")
    bookmark = relationship("Bookmark", back_populates="collection_items")
    
    __table_args__ = (
        UniqueConstraint("collection_id", "bookmark_id", name="unique_collection_item"),
    )

