"""Content progress tracking model."""
from datetime import datetime
from typing import Optional
from enum import Enum
from sqlalchemy import (
    String,
    Integer,
    ForeignKey,
    DateTime,
    UniqueConstraint,
    Index,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from app.models.base import TimestampMixin


class ProgressStatus(str, Enum):
    """Status of content progress."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class ContentProgress(Base, TimestampMixin):
    """Track user progress on any content type."""
    
    __tablename__ = "content_progress"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    content_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    content_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    
    # Progress tracking
    status: Mapped[str] = mapped_column(
        String(20),
        default=ProgressStatus.NOT_STARTED.value,
        nullable=False,
    )
    progress_percentage: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Timestamps
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_accessed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Time spent (in seconds)
    time_spent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="content_progress")
    
    __table_args__ = (
        UniqueConstraint("user_id", "content_type", "content_id", name="unique_user_content_progress"),
        Index("idx_progress_content", "content_type", "content_id"),
        Index("idx_progress_user_status", "user_id", "status"),
    )

