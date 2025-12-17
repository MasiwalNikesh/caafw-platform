"""Research papers API endpoints."""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.db.database import get_db
from app.models.research import ResearchPaper, PaperAuthor
from app.schemas.research import ResearchPaperResponse, ResearchListResponse

router = APIRouter()


@router.get("", response_model=ResearchListResponse)
async def list_papers(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    source: Optional[str] = None,
    category: Optional[str] = None,
    has_code: Optional[bool] = None,
    is_featured: Optional[bool] = None,
    search: Optional[str] = None,
    sort_by: str = Query(default="published_at", pattern="^(published_at|citations|stars)$"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db),
):
    """List research papers with filtering and pagination."""
    query = select(ResearchPaper)

    # Apply filters
    if source:
        query = query.where(ResearchPaper.source == source)
    if category:
        query = query.where(ResearchPaper.primary_category == category)
    if has_code is not None:
        query = query.where(ResearchPaper.has_code == has_code)
    if is_featured is not None:
        query = query.where(ResearchPaper.is_featured == is_featured)
    if search:
        query = query.where(
            ResearchPaper.title.ilike(f"%{search}%") |
            ResearchPaper.abstract.ilike(f"%{search}%")
        )

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    # Apply sorting
    sort_column = getattr(ResearchPaper, sort_by)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc().nullslast())
    else:
        query = query.order_by(sort_column.asc().nullsfirst())

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    query = query.options(selectinload(ResearchPaper.authors))

    result = await db.execute(query)
    papers = result.scalars().all()

    total_pages = (total + page_size - 1) // page_size

    return ResearchListResponse(
        items=[ResearchPaperResponse.model_validate(p) for p in papers],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )


@router.get("/categories", response_model=List[str])
async def list_categories(db: AsyncSession = Depends(get_db)):
    """List available paper categories."""
    query = (
        select(ResearchPaper.primary_category)
        .distinct()
        .where(ResearchPaper.primary_category.isnot(None))
        .order_by(ResearchPaper.primary_category)
    )
    result = await db.execute(query)
    return [row[0] for row in result.all()]


@router.get("/{paper_id}", response_model=ResearchPaperResponse)
async def get_paper(
    paper_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a single research paper by ID."""
    query = (
        select(ResearchPaper)
        .where(ResearchPaper.id == paper_id)
        .options(selectinload(ResearchPaper.authors))
    )
    result = await db.execute(query)
    paper = result.scalar_one_or_none()

    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    return ResearchPaperResponse.model_validate(paper)


@router.get("/arxiv/{arxiv_id}", response_model=ResearchPaperResponse)
async def get_paper_by_arxiv_id(
    arxiv_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a research paper by arXiv ID."""
    query = (
        select(ResearchPaper)
        .where(ResearchPaper.arxiv_id == arxiv_id)
        .options(selectinload(ResearchPaper.authors))
    )
    result = await db.execute(query)
    paper = result.scalar_one_or_none()

    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    return ResearchPaperResponse.model_validate(paper)
