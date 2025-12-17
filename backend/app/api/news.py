"""News API endpoints."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.database import get_db
from app.models.news import NewsArticle, NewsSource
from app.schemas.news import NewsArticleResponse, NewsListResponse

router = APIRouter()


@router.get("", response_model=NewsListResponse)
async def list_news(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    source: Optional[str] = None,
    category: Optional[str] = None,
    is_featured: Optional[bool] = None,
    search: Optional[str] = None,
    sort_by: str = Query(default="published_at", pattern="^(published_at|created_at|views)$"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db),
):
    """List news articles with filtering and pagination."""
    query = select(NewsArticle).where(NewsArticle.is_active == True)

    # Apply filters
    if source:
        query = query.where(NewsArticle.source == source)
    if category:
        query = query.where(NewsArticle.category == category)
    if is_featured is not None:
        query = query.where(NewsArticle.is_featured == is_featured)
    if search:
        query = query.where(
            NewsArticle.title.ilike(f"%{search}%") |
            NewsArticle.summary.ilike(f"%{search}%")
        )

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    # Apply sorting
    sort_column = getattr(NewsArticle, sort_by)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc().nullslast())
    else:
        query = query.order_by(sort_column.asc().nullsfirst())

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    articles = result.scalars().all()

    total_pages = (total + page_size - 1) // page_size

    return NewsListResponse(
        items=[NewsArticleResponse.model_validate(a) for a in articles],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )


@router.get("/sources", response_model=list)
async def list_sources():
    """List available news sources."""
    return [{"value": s.value, "label": s.name.replace("_", " ").title()} for s in NewsSource]


@router.get("/{article_id}", response_model=NewsArticleResponse)
async def get_article(
    article_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a single news article by ID."""
    query = select(NewsArticle).where(
        NewsArticle.id == article_id,
        NewsArticle.is_active == True
    )
    result = await db.execute(query)
    article = result.scalar_one_or_none()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    # Increment views
    article.views += 1
    await db.commit()

    return NewsArticleResponse.model_validate(article)
