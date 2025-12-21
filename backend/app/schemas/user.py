"""User and profile schemas."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from .common import BaseResponse


# ============== Request Schemas ==============

class UserCreate(BaseModel):
    """Schema for user registration."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    name: Optional[str] = Field(None, max_length=255)


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class ProfileUpdate(BaseModel):
    """Schema for updating user profile."""
    name: Optional[str] = Field(None, max_length=255)
    auto_filter_content: Optional[bool] = None
    interests: Optional[List[str]] = None
    learning_goals: Optional[List[str]] = None


# ============== Response Schemas ==============

class UserResponse(BaseResponse):
    """User response schema (without sensitive data)."""
    id: int
    email: str
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_verified: bool = False
    created_at: datetime


class UserProfileResponse(BaseResponse):
    """User profile response schema."""
    id: int
    user_id: int
    ai_level: Optional[str] = None  # novice, beginner, intermediate, expert
    ai_level_score: Optional[int] = None  # 0-100
    has_completed_quiz: bool = False
    auto_filter_content: bool = True
    interests: Optional[List[str]] = None
    learning_goals: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime


class UserWithProfileResponse(UserResponse):
    """User with profile response."""
    profile: Optional[UserProfileResponse] = None


class TokenResponse(BaseModel):
    """Token response schema after login/register."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
