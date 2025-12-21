"""Real-time updates API endpoints."""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.database import get_db
from app.models.job import Job
from app.models.learning import LearningResource
from app.models.event import Event
from app.models.research import ResearchPaper

router = APIRouter()


@router.get("/check")
async def check_updates(
    since: Optional[str] = Query(None, description="ISO timestamp to check updates since"),
    db: AsyncSession = Depends(get_db),
):
    """
    Check for new content since a given timestamp.
    Returns counts of new items in each category.
    Used for polling-based real-time updates.
    """
    # Default to last 5 minutes if no timestamp provided
    if since:
        try:
            since_dt = datetime.fromisoformat(since.replace('Z', '+00:00'))
        except ValueError:
            since_dt = datetime.utcnow() - timedelta(minutes=5)
    else:
        since_dt = datetime.utcnow() - timedelta(minutes=5)

    # Count new items in each category
    jobs_count = await db.scalar(
        select(func.count()).select_from(
            select(Job).where(Job.created_at > since_dt).subquery()
        )
    )

    learning_count = await db.scalar(
        select(func.count()).select_from(
            select(LearningResource).where(LearningResource.created_at > since_dt).subquery()
        )
    )

    events_count = await db.scalar(
        select(func.count()).select_from(
            select(Event).where(Event.created_at > since_dt).subquery()
        )
    )

    research_count = await db.scalar(
        select(func.count()).select_from(
            select(ResearchPaper).where(ResearchPaper.created_at > since_dt).subquery()
        )
    )

    total = (jobs_count or 0) + (learning_count or 0) + (events_count or 0) + (research_count or 0)

    return {
        "has_updates": total > 0,
        "total_new": total,
        "categories": {
            "jobs": jobs_count or 0,
            "learning": learning_count or 0,
            "events": events_count or 0,
            "research": research_count or 0,
        },
        "checked_at": datetime.utcnow().isoformat(),
        "since": since_dt.isoformat(),
    }


@router.get("/latest")
async def get_latest_timestamps(
    db: AsyncSession = Depends(get_db),
):
    """
    Get the latest update timestamps for each category.
    Useful for determining if any data has changed.
    """
    jobs_latest = await db.scalar(
        select(func.max(Job.created_at))
    )

    learning_latest = await db.scalar(
        select(func.max(LearningResource.created_at))
    )

    events_latest = await db.scalar(
        select(func.max(Event.created_at))
    )

    research_latest = await db.scalar(
        select(func.max(ResearchPaper.created_at))
    )

    return {
        "timestamps": {
            "jobs": jobs_latest.isoformat() if jobs_latest else None,
            "learning": learning_latest.isoformat() if learning_latest else None,
            "events": events_latest.isoformat() if events_latest else None,
            "research": research_latest.isoformat() if research_latest else None,
        },
        "checked_at": datetime.utcnow().isoformat(),
    }
