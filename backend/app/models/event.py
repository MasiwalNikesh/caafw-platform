"""Event models."""
from datetime import datetime
from typing import Optional, List
from enum import Enum
from sqlalchemy import String, Text, Integer, Float, Boolean, JSON, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base
from .base import TimestampMixin


class EventType(str, Enum):
    """Event type enum."""
    CONFERENCE = "conference"
    MEETUP = "meetup"
    WORKSHOP = "workshop"
    WEBINAR = "webinar"
    HACKATHON = "hackathon"
    SUMMIT = "summit"
    OTHER = "other"


class Event(Base, TimestampMixin):
    """Event model."""

    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    external_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True)
    source: Mapped[str] = mapped_column(String(50), nullable=False)  # eventbrite, meetup, luma, etc.
    event_type: Mapped[EventType] = mapped_column(SQLEnum(EventType), default=EventType.OTHER)

    # Basic Info
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    slug: Mapped[str] = mapped_column(String(550), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    short_description: Mapped[Optional[str]] = mapped_column(String(500))

    # Organizer
    organizer_name: Mapped[Optional[str]] = mapped_column(String(255))
    organizer_url: Mapped[Optional[str]] = mapped_column(String(500))

    # Location
    venue_name: Mapped[Optional[str]] = mapped_column(String(255))
    address: Mapped[Optional[str]] = mapped_column(Text)
    city: Mapped[Optional[str]] = mapped_column(String(100))
    state: Mapped[Optional[str]] = mapped_column(String(100))
    country: Mapped[Optional[str]] = mapped_column(String(100))
    latitude: Mapped[Optional[float]] = mapped_column(Float)
    longitude: Mapped[Optional[float]] = mapped_column(Float)
    is_online: Mapped[bool] = mapped_column(Boolean, default=False)
    online_url: Mapped[Optional[str]] = mapped_column(String(500))

    # URLs
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    registration_url: Mapped[Optional[str]] = mapped_column(String(500))
    image_url: Mapped[Optional[str]] = mapped_column(String(500))

    # Pricing
    is_free: Mapped[bool] = mapped_column(Boolean, default=False)
    price_min: Mapped[Optional[float]] = mapped_column(Float)
    price_max: Mapped[Optional[float]] = mapped_column(Float)
    currency: Mapped[Optional[str]] = mapped_column(String(10), default="USD")

    # Capacity
    capacity: Mapped[Optional[int]] = mapped_column(Integer)
    attendees_count: Mapped[int] = mapped_column(Integer, default=0)

    # Topics
    topics: Mapped[Optional[List[str]]] = mapped_column(JSON)
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON)

    # Speakers
    speakers: Mapped[Optional[List[dict]]] = mapped_column(JSON)

    # Status
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped[Optional[str]] = mapped_column(String(50))  # upcoming, live, ended, cancelled

    # AI Readiness Level (for personalization)
    level: Mapped[Optional[str]] = mapped_column(String(20))  # novice, beginner, intermediate, expert

    # Dates
    starts_at: Mapped[Optional[datetime]] = mapped_column()
    ends_at: Mapped[Optional[datetime]] = mapped_column()
    timezone: Mapped[Optional[str]] = mapped_column(String(50))

    # Extra data
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON)

    def __repr__(self) -> str:
        return f"<Event {self.title[:50]}...>"
