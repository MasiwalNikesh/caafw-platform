"""Events API endpoints."""
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.database import get_db, AsyncSessionLocal
from app.models.event import Event, EventType
from app.schemas.event import EventResponse, EventListResponse
from app.collectors.ai_events import AIEventsCollector

router = APIRouter()


@router.get("", response_model=EventListResponse)
async def list_events(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    event_type: Optional[str] = None,
    is_online: Optional[bool] = None,
    is_free: Optional[bool] = None,
    city: Optional[str] = None,
    country: Optional[str] = None,
    is_featured: Optional[bool] = None,
    upcoming_only: bool = Query(default=True),
    search: Optional[str] = None,
    sort_by: str = Query(default="starts_at", pattern="^(starts_at|created_at|attendees_count)$"),
    sort_order: str = Query(default="asc", pattern="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db),
):
    """List events with filtering and pagination."""
    query = select(Event).where(Event.is_active == True)

    # Filter for upcoming events
    if upcoming_only:
        query = query.where(Event.starts_at >= datetime.utcnow())

    # Apply filters
    if event_type:
        query = query.where(Event.event_type == event_type)
    if is_online is not None:
        query = query.where(Event.is_online == is_online)
    if is_free is not None:
        query = query.where(Event.is_free == is_free)
    if city:
        query = query.where(Event.city.ilike(f"%{city}%"))
    if country:
        query = query.where(Event.country.ilike(f"%{country}%"))
    if is_featured is not None:
        query = query.where(Event.is_featured == is_featured)
    if search:
        query = query.where(
            Event.title.ilike(f"%{search}%") |
            Event.description.ilike(f"%{search}%")
        )

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    # Apply sorting
    sort_column = getattr(Event, sort_by)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc().nullslast())
    else:
        query = query.order_by(sort_column.asc().nullsfirst())

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    events = result.scalars().all()

    total_pages = (total + page_size - 1) // page_size

    return EventListResponse(
        items=[EventResponse.model_validate(e) for e in events],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )


@router.get("/types", response_model=List[dict])
async def list_event_types():
    """List available event types."""
    return [{"value": t.value, "label": t.name.title()} for t in EventType]


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a single event by ID."""
    query = select(Event).where(Event.id == event_id, Event.is_active == True)
    result = await db.execute(query)
    event = result.scalar_one_or_none()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    return EventResponse.model_validate(event)


@router.post("/collect", tags=["Collection"])
async def collect_events(
    include_recurring: bool = Query(default=True, description="Include recurring meetups and webinars"),
):
    """Collect AI conferences, meetups, and workshops."""
    collector = AIEventsCollector()

    try:
        # Collect events
        raw_data = await collector.collect(include_recurring=include_recurring)

        if not raw_data:
            return {"message": "No events collected", "collected": 0, "inserted": 0}

        # Transform data
        transformed_data = await collector.transform(raw_data)

        # Upsert into database
        async with AsyncSessionLocal() as session:
            inserted = 0
            updated = 0

            for item in transformed_data:
                # Check if exists
                db_query = select(Event).where(Event.external_id == item.get("external_id"))
                result = await session.execute(db_query)
                existing = result.scalar_one_or_none()

                if existing:
                    # Update existing event
                    for key, value in item.items():
                        if hasattr(existing, key) and key != "id":
                            setattr(existing, key, value)
                    updated += 1
                else:
                    # Insert new event
                    new_event = Event(**item)
                    session.add(new_event)
                    inserted += 1

            await session.commit()

        return {
            "message": "Collection complete",
            "collected": len(transformed_data),
            "inserted": inserted,
            "updated": updated,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Collection failed: {str(e)}")
