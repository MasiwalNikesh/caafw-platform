"""Quiz models."""
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from enum import Enum
from sqlalchemy import String, Text, Integer, Boolean, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from .base import TimestampMixin

if TYPE_CHECKING:
    from .user import User


class QuestionType(str, Enum):
    """Quiz question type."""
    MULTIPLE_CHOICE = "multiple_choice"
    SELF_ASSESSMENT = "self_assessment"
    MULTI_SELECT = "multi_select"


class QuestionCategory(str, Enum):
    """Question category for non-technical AI readiness assessment."""
    AWARENESS = "awareness"          # AI awareness & familiarity
    DAILY_LIFE = "daily_life"        # AI in daily life usage
    GOALS = "goals"                  # Learning & goals
    PROFESSIONAL = "professional"    # Professional context
    COMFORT = "comfort"              # Comfort level with AI


class QuizQuestion(Base, TimestampMixin):
    """Quiz question model."""

    __tablename__ = "quiz_questions"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Question content
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[str] = mapped_column(String(50), nullable=False)  # multiple_choice, self_assessment, multi_select
    category: Mapped[str] = mapped_column(String(50), nullable=False)  # awareness, daily_life, goals, professional, comfort

    # For multiple choice / multi-select
    options: Mapped[Optional[List[dict]]] = mapped_column(JSON)  # [{"id": "a", "text": "...", "score": 10}]

    # For self-assessment (1-5 scale)
    scale_labels: Mapped[Optional[dict]] = mapped_column(JSON)  # {"1": "Never", "5": "Expert"}

    # Scoring weight (some questions worth more)
    weight: Mapped[int] = mapped_column(Integer, default=1)

    # Status and ordering
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    order: Mapped[int] = mapped_column(Integer, default=0)


class QuizResult(Base, TimestampMixin):
    """User quiz result."""

    __tablename__ = "quiz_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    # Scores
    total_score: Mapped[int] = mapped_column(Integer, nullable=False)
    max_possible_score: Mapped[int] = mapped_column(Integer, nullable=False)
    percentage: Mapped[int] = mapped_column(Integer, nullable=False)

    # Computed level
    computed_level: Mapped[str] = mapped_column(String(20), nullable=False)  # novice, beginner, intermediate, expert

    # Detailed answers
    answers: Mapped[List[dict]] = mapped_column(JSON, nullable=False)
    # [{"question_id": 1, "answer": "a", "score": 10}]

    # Category scores (percentages)
    category_scores: Mapped[Optional[dict]] = mapped_column(JSON)
    # {"awareness": 80, "daily_life": 60, ...}

    # Relationship
    user: Mapped["User"] = relationship(back_populates="quiz_results")
