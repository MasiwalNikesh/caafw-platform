"""Admin dashboard API endpoints."""
from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

from app.db.database import get_db
from app.models.user import User
from app.models.admin import ContentStatus, AuditLog, APISource
from app.models.news import NewsArticle
from app.models.job import Job
from app.models.product import Product
from app.models.event import Event
from app.models.research import ResearchPaper
from app.core.deps import get_current_admin
from app.schemas.admin import (
    DashboardStats,
    DashboardResponse,
    PendingReviewItem,
    RecentActivityItem,
    SourceHealthItem,
    PendingReviewStats,
    ContentStats,
    APISourceStats,
)

router = APIRouter()


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Get dashboard statistics."""
    today = datetime.utcnow().date()
    today_start = datetime.combine(today, datetime.min.time())
    week_start = today_start - timedelta(days=7)

    # Count pending items across content types
    pending_news = await db.scalar(
        select(func.count(NewsArticle.id)).where(
            NewsArticle.moderation_status == ContentStatus.PENDING
        )
    )
    pending_jobs = await db.scalar(
        select(func.count(Job.id)).where(
            Job.moderation_status == ContentStatus.PENDING
        )
    )
    pending_products = await db.scalar(
        select(func.count(Product.id)).where(
            Product.moderation_status == ContentStatus.PENDING
        )
    )
    pending_events = await db.scalar(
        select(func.count(Event.id)).where(
            Event.moderation_status == ContentStatus.PENDING
        )
    )
    pending_review = (pending_news or 0) + (pending_jobs or 0) + (pending_products or 0) + (pending_events or 0)

    # Total users
    total_users = await db.scalar(select(func.count(User.id)))

    # Total content
    total_news = await db.scalar(select(func.count(NewsArticle.id)))
    total_jobs = await db.scalar(select(func.count(Job.id)))
    total_products = await db.scalar(select(func.count(Product.id)))
    total_events = await db.scalar(select(func.count(Event.id)))
    total_research = await db.scalar(select(func.count(ResearchPaper.id)))
    total_content = (total_news or 0) + (total_jobs or 0) + (total_products or 0) + (total_events or 0) + (total_research or 0)

    # API sources status
    active_sources = await db.scalar(
        select(func.count(APISource.id)).where(APISource.is_active == True)
    )
    failed_sources = await db.scalar(
        select(func.count(APISource.id)).where(
            and_(APISource.is_active == True, APISource.error_count > 0)
        )
    )

    # Today's moderation activity
    today_approvals = await db.scalar(
        select(func.count(AuditLog.id)).where(
            and_(
                AuditLog.action == "approve_content",
                AuditLog.created_at >= today_start
            )
        )
    )
    today_rejections = await db.scalar(
        select(func.count(AuditLog.id)).where(
            and_(
                AuditLog.action == "reject_content",
                AuditLog.created_at >= today_start
            )
        )
    )

    # New users
    new_users_today = await db.scalar(
        select(func.count(User.id)).where(User.created_at >= today_start)
    )
    new_users_this_week = await db.scalar(
        select(func.count(User.id)).where(User.created_at >= week_start)
    )

    return DashboardStats(
        pending_review=PendingReviewStats(
            news=pending_news or 0,
            jobs=pending_jobs or 0,
            products=pending_products or 0,
            events=pending_events or 0,
            research=0,  # Research doesn't have moderation
            total=pending_review,
        ),
        total_users=total_users or 0,
        total_content=ContentStats(
            news=total_news or 0,
            jobs=total_jobs or 0,
            products=total_products or 0,
            events=total_events or 0,
            research=total_research or 0,
        ),
        api_sources=APISourceStats(
            active=active_sources or 0,
            with_errors=failed_sources or 0,
        ),
        today_approvals=today_approvals or 0,
        today_rejections=today_rejections or 0,
        new_users_today=new_users_today or 0,
        new_users_this_week=new_users_this_week or 0,
    )


@router.get("/pending-review", response_model=List[PendingReviewItem])
async def get_pending_review(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Get items pending review."""
    pending_items = []

    # Get pending news
    news_query = (
        select(NewsArticle)
        .where(NewsArticle.moderation_status == ContentStatus.PENDING)
        .order_by(NewsArticle.created_at.desc())
        .limit(limit)
    )
    news_result = await db.execute(news_query)
    for article in news_result.scalars():
        pending_items.append(PendingReviewItem(
            id=article.id,
            content_type="news",
            title=article.title,
            source=article.source.value,
            created_at=article.created_at,
            url=article.url,
        ))

    # Get pending jobs
    jobs_query = (
        select(Job)
        .where(Job.moderation_status == ContentStatus.PENDING)
        .order_by(Job.created_at.desc())
        .limit(limit)
    )
    jobs_result = await db.execute(jobs_query)
    for job in jobs_result.scalars():
        pending_items.append(PendingReviewItem(
            id=job.id,
            content_type="job",
            title=f"{job.title} at {job.company_name}",
            source=job.source.value,
            created_at=job.created_at,
            url=job.apply_url,
        ))

    # Get pending products
    products_query = (
        select(Product)
        .where(Product.moderation_status == ContentStatus.PENDING)
        .order_by(Product.created_at.desc())
        .limit(limit)
    )
    products_result = await db.execute(products_query)
    for product in products_result.scalars():
        pending_items.append(PendingReviewItem(
            id=product.id,
            content_type="product",
            title=product.name,
            source=product.source,
            created_at=product.created_at,
            url=product.website_url,
        ))

    # Get pending events
    events_query = (
        select(Event)
        .where(Event.moderation_status == ContentStatus.PENDING)
        .order_by(Event.created_at.desc())
        .limit(limit)
    )
    events_result = await db.execute(events_query)
    for event in events_result.scalars():
        pending_items.append(PendingReviewItem(
            id=event.id,
            content_type="event",
            title=event.title,
            source=event.source,
            created_at=event.created_at,
            url=event.url,
        ))

    # Sort by created_at and limit
    pending_items.sort(key=lambda x: x.created_at, reverse=True)
    return pending_items[:limit]


@router.get("/recent-activity", response_model=List[RecentActivityItem])
async def get_recent_activity(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Get recent admin activity."""
    query = (
        select(AuditLog, User.name, User.email)
        .join(User, AuditLog.admin_id == User.id)
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(query)

    activities = []
    for audit_log, admin_name, admin_email in result:
        activities.append(RecentActivityItem(
            id=audit_log.id,
            admin_name=admin_name or admin_email,
            action=audit_log.action,
            entity_type=audit_log.entity_type,
            entity_title=audit_log.new_values.get("title") if audit_log.new_values else None,
            created_at=audit_log.created_at,
        ))

    return activities


@router.get("/source-health", response_model=List[SourceHealthItem])
async def get_source_health(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Get API source health status."""
    query = select(APISource).order_by(APISource.name)
    result = await db.execute(query)

    sources = []
    now = datetime.utcnow()

    for source in result.scalars():
        # Determine health status
        if not source.is_active:
            status = "inactive"
        elif source.error_count >= 5:
            status = "error"
        elif source.error_count > 0:
            status = "warning"
        elif source.last_fetched_at and (now - source.last_fetched_at).total_seconds() > source.fetch_frequency * 60 * 2:
            status = "warning"  # Overdue fetch
        else:
            status = "ok"

        sources.append(SourceHealthItem(
            id=source.id,
            name=source.name,
            source_type=source.source_type,
            is_active=source.is_active,
            last_fetched_at=source.last_fetched_at,
            last_error=source.last_error,
            error_count=source.error_count,
            status=status,
        ))

    return sources


@router.get("", response_model=DashboardResponse)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Get complete dashboard data."""
    stats = await get_dashboard_stats(db=db, admin=admin)
    pending_review = await get_pending_review(limit=10, db=db, admin=admin)
    recent_activity = await get_recent_activity(limit=10, db=db, admin=admin)
    source_health = await get_source_health(db=db, admin=admin)

    return DashboardResponse(
        stats=stats,
        pending_review=pending_review,
        recent_activity=recent_activity,
        source_health=source_health,
    )
