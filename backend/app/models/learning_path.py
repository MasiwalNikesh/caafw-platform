"""Learning path models."""
from datetime import datetime
from typing import Optional, List
from enum import Enum
from sqlalchemy import String, Text, Integer, Boolean, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from .base import TimestampMixin


class PathLevel(str, Enum):
    """Learning path level enum."""
    NOVICE = "novice"
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    EXPERT = "expert"


class LearningPath(Base, TimestampMixin):
    """Learning path model - curated sequence of learning resources."""

    __tablename__ = "learning_paths"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(300), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    level: Mapped[str] = mapped_column(String(20), nullable=False)  # novice, beginner, intermediate, expert
    duration_hours: Mapped[Optional[int]] = mapped_column(Integer)
    topics: Mapped[Optional[List[str]]] = mapped_column(JSON)
    resource_ids: Mapped[List[int]] = mapped_column(JSON, nullable=False)  # Ordered array of resource IDs
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    user_progress: Mapped[List["UserLearningProgress"]] = relationship(
        "UserLearningProgress", back_populates="path", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<LearningPath {self.title}>"


class UserLearningProgress(Base, TimestampMixin):
    """User progress on a learning path."""

    __tablename__ = "user_learning_progress"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    path_id: Mapped[int] = mapped_column(ForeignKey("learning_paths.id", ondelete="CASCADE"), nullable=False)
    completed_resource_ids: Mapped[List[int]] = mapped_column(JSON, default=list)
    current_resource_id: Mapped[Optional[int]] = mapped_column(Integer)
    progress_percentage: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[Optional[datetime]] = mapped_column()
    last_activity_at: Mapped[Optional[datetime]] = mapped_column()
    completed_at: Mapped[Optional[datetime]] = mapped_column()

    # Relationships
    path: Mapped["LearningPath"] = relationship("LearningPath", back_populates="user_progress")

    def __repr__(self) -> str:
        return f"<UserLearningProgress user={self.user_id} path={self.path_id} {self.progress_percentage}%>"
