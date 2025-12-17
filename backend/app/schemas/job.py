"""Job schemas."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from .common import BaseResponse, PaginatedResponse


class JobBase(BaseModel):
    """Base job schema."""

    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    company_name: str = Field(..., min_length=1, max_length=255)
    location: Optional[str] = None
    is_remote: bool = False
    job_type: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    skills: Optional[List[str]] = None


class JobCreate(JobBase):
    """Schema for creating a job."""

    slug: str = Field(..., min_length=1, max_length=300)
    source: str = Field(default="manual")
    description_html: Optional[str] = None
    company_logo: Optional[str] = None
    company_url: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    is_hybrid: bool = False
    experience_level: Optional[str] = None
    salary_currency: str = "USD"
    requirements: Optional[List[str]] = None
    benefits: Optional[List[str]] = None
    apply_url: Optional[str] = None


class JobUpdate(BaseModel):
    """Schema for updating a job."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    company_name: Optional[str] = None
    location: Optional[str] = None
    is_remote: Optional[bool] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    skills: Optional[List[str]] = None


class JobResponse(BaseResponse):
    """Job response schema."""

    id: int
    title: str
    slug: str
    description: Optional[str] = None
    source: str
    company_name: str
    company_logo: Optional[str] = None
    company_url: Optional[str] = None
    location: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    is_remote: bool = False
    is_hybrid: bool = False
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: str = "USD"
    skills: Optional[List[str]] = None
    requirements: Optional[List[str]] = None
    benefits: Optional[List[str]] = None
    apply_url: Optional[str] = None
    is_featured: bool = False
    is_active: bool = True
    posted_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class JobListResponse(PaginatedResponse[JobResponse]):
    """Paginated job list response."""

    pass
