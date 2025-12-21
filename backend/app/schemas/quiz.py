"""Quiz schemas."""
from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from .common import BaseResponse


# ============== Request Schemas ==============

class QuizAnswerSubmit(BaseModel):
    """Single answer submission."""
    question_id: int
    answer: str  # "a", "b", etc. or "1"-"5" for self-assessment, or comma-separated for multi-select


class QuizSubmission(BaseModel):
    """Full quiz submission."""
    answers: List[QuizAnswerSubmit]


# ============== Response Schemas ==============

class QuizQuestionOption(BaseModel):
    """Quiz question option."""
    id: str
    text: str
    score: Optional[int] = None  # Not exposed to client


class QuizQuestionResponse(BaseResponse):
    """Quiz question response (without correct answers)."""
    id: int
    question_text: str
    question_type: str  # multiple_choice, self_assessment, multi_select
    category: str  # awareness, daily_life, goals, professional, comfort
    options: Optional[List[Dict]] = None  # For multiple choice / multi-select
    scale_labels: Optional[Dict[str, str]] = None  # For self-assessment
    order: int


class QuizResultResponse(BaseResponse):
    """Quiz result response."""
    id: int
    total_score: int
    max_possible_score: int
    percentage: int
    computed_level: str  # novice, beginner, intermediate, expert
    category_scores: Optional[Dict[str, int]] = None
    created_at: datetime


class QuizResultDetailResponse(QuizResultResponse):
    """Detailed quiz result with answers (for review)."""
    answers: List[Dict]
