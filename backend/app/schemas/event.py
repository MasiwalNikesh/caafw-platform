"""Event schemas."""
from datetime import datetime
from typing import Optional, List
from .common import BaseResponse, PaginatedResponse


class EventResponse(BaseResponse):
    """Event response schema."""

    id: int
    title: str
    slug: str
    description: Optional[str] = None
    short_description: Optional[str] = None
    source: str
    event_type: str
    organizer_name: Optional[str] = None
    organizer_url: Optional[str] = None
    venue_name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_online: bool = False
    online_url: Optional[str] = None
    url: str
    registration_url: Optional[str] = None
    image_url: Optional[str] = None
    is_free: bool = False
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    currency: str = "USD"
    capacity: Optional[int] = None
    attendees_count: int = 0
    topics: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    speakers: Optional[List[dict]] = None
    is_featured: bool = False
    status: Optional[str] = None
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None
    timezone: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class EventListResponse(PaginatedResponse[EventResponse]):
    """Paginated event list response."""

    pass
