"""User and profile models."""
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from enum import Enum
from sqlalchemy import String, Text, Boolean, Integer, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from .base import TimestampMixin
from .admin import UserRole

if TYPE_CHECKING:
    from .quiz import QuizResult
    from .bookmark import Bookmark, Collection
    from .content_progress import ContentProgress


class UserLevel(str, Enum):
    """User AI readiness level."""
    NOVICE = "novice"
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    EXPERT = "expert"


class User(Base, TimestampMixin):
    """User model - email-based and OAuth authentication."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Nullable for OAuth users

    # OAuth fields
    oauth_provider: Mapped[Optional[str]] = mapped_column(String(20))  # google, microsoft, linkedin
    oauth_id: Mapped[Optional[str]] = mapped_column(String(255))  # OAuth provider's user ID
    oauth_email_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # Profile info
    name: Mapped[Optional[str]] = mapped_column(String(255))
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500))

    # Role and permissions
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole, values_callable=lambda x: [e.value for e in x]),
        default=UserRole.USER,
        nullable=False
    )

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # Ban status
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)
    banned_reason: Mapped[Optional[str]] = mapped_column(Text)
    banned_at: Mapped[Optional[datetime]] = mapped_column()
    banned_by_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))

    # Timestamps
    last_login_at: Mapped[Optional[datetime]] = mapped_column()

    # Relationships
    profile: Mapped["UserProfile"] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    quiz_results: Mapped[List["QuizResult"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )
    bookmarks: Mapped[List["Bookmark"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )
    collections: Mapped[List["Collection"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )
    content_progress: Mapped[List["ContentProgress"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )


class UserProfile(Base, TimestampMixin):
    """User profile with quiz results and preferences."""

    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)

    # AI Level (computed from quiz)
    ai_level: Mapped[Optional[str]] = mapped_column(String(20))  # novice, beginner, intermediate, expert
    ai_level_score: Mapped[Optional[int]] = mapped_column(Integer)  # 0-100

    # Preferences
    has_completed_quiz: Mapped[bool] = mapped_column(Boolean, default=False)
    auto_filter_content: Mapped[bool] = mapped_column(Boolean, default=True)

    # Interest areas and goals
    interests: Mapped[Optional[List[str]]] = mapped_column(JSON)
    learning_goals: Mapped[Optional[List[str]]] = mapped_column(JSON)

    # Relationship
    user: Mapped["User"] = relationship(back_populates="profile")
