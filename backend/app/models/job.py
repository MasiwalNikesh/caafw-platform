"""Job listing models."""
from datetime import datetime
from typing import Optional, List
from enum import Enum
from sqlalchemy import String, Text, Integer, Boolean, JSON, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base
from .base import TimestampMixin


class JobSource(str, Enum):
    """Job data source enum."""
    ADZUNA = "ADZUNA"
    THE_MUSE = "THE_MUSE"
    USA_JOBS = "USA_JOBS"
    REMOTE_OK = "REMOTE_OK"
    WELLFOUND = "WELLFOUND"
    LINKEDIN = "LINKEDIN"
    INDEED = "INDEED"
    MANUAL = "MANUAL"
    curated = "curated"


class Job(Base, TimestampMixin):
    """Job listing model."""

    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    external_id: Mapped[Optional[str]] = mapped_column(String(100))
    source: Mapped[JobSource] = mapped_column(SQLEnum(JobSource), nullable=False)

    # Basic Info
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    description_html: Mapped[Optional[str]] = mapped_column(Text)

    # Company
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    company_logo: Mapped[Optional[str]] = mapped_column(String(500))
    company_url: Mapped[Optional[str]] = mapped_column(String(500))

    # Location
    location: Mapped[Optional[str]] = mapped_column(String(255))
    city: Mapped[Optional[str]] = mapped_column(String(100))
    state: Mapped[Optional[str]] = mapped_column(String(100))
    country: Mapped[Optional[str]] = mapped_column(String(100))
    is_remote: Mapped[bool] = mapped_column(Boolean, default=False)
    is_hybrid: Mapped[bool] = mapped_column(Boolean, default=False)

    # Employment Type
    job_type: Mapped[Optional[str]] = mapped_column(String(50))  # full-time, part-time, contract
    experience_level: Mapped[Optional[str]] = mapped_column(String(50))  # entry, mid, senior

    # Salary
    salary_min: Mapped[Optional[int]] = mapped_column(Integer)
    salary_max: Mapped[Optional[int]] = mapped_column(Integer)
    salary_currency: Mapped[Optional[str]] = mapped_column(String(10), default="USD")

    # Requirements
    skills: Mapped[Optional[List[str]]] = mapped_column(JSON)
    requirements: Mapped[Optional[List[str]]] = mapped_column(JSON)
    benefits: Mapped[Optional[List[str]]] = mapped_column(JSON)

    # URLs
    apply_url: Mapped[Optional[str]] = mapped_column(String(500))
    source_url: Mapped[Optional[str]] = mapped_column(String(500))

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)

    # Dates
    posted_at: Mapped[Optional[datetime]] = mapped_column()
    expires_at: Mapped[Optional[datetime]] = mapped_column()

    # Extra data
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON)

    def __repr__(self) -> str:
        return f"<Job {self.title} at {self.company_name}>"
