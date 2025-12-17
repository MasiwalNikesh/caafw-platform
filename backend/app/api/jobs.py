"""Jobs API endpoints."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.database import get_db, AsyncSessionLocal
from app.models.job import Job, JobSource
from app.schemas.job import JobCreate, JobUpdate, JobResponse, JobListResponse
from app.collectors.ai_jobs import AIJobsCollector

router = APIRouter()


@router.get("", response_model=JobListResponse)
async def list_jobs(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    source: Optional[str] = None,
    company: Optional[str] = None,
    location: Optional[str] = None,
    is_remote: Optional[bool] = None,
    job_type: Optional[str] = None,
    experience_level: Optional[str] = None,
    salary_min: Optional[int] = None,
    search: Optional[str] = None,
    sort_by: str = Query(default="posted_at", pattern="^(posted_at|created_at|salary_max)$"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db),
):
    """List jobs with filtering and pagination."""
    query = select(Job).where(Job.is_active == True)

    # Apply filters
    if source:
        query = query.where(Job.source == source)
    if company:
        query = query.where(Job.company_name.ilike(f"%{company}%"))
    if location:
        query = query.where(
            Job.location.ilike(f"%{location}%") |
            Job.city.ilike(f"%{location}%") |
            Job.country.ilike(f"%{location}%")
        )
    if is_remote is not None:
        query = query.where(Job.is_remote == is_remote)
    if job_type:
        query = query.where(Job.job_type == job_type)
    if experience_level:
        query = query.where(Job.experience_level == experience_level)
    if salary_min:
        query = query.where(Job.salary_max >= salary_min)
    if search:
        query = query.where(
            Job.title.ilike(f"%{search}%") |
            Job.description.ilike(f"%{search}%") |
            Job.company_name.ilike(f"%{search}%")
        )

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    # Apply sorting
    sort_column = getattr(Job, sort_by)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc().nullslast())
    else:
        query = query.order_by(sort_column.asc().nullsfirst())

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    jobs = result.scalars().all()

    total_pages = (total + page_size - 1) // page_size

    return JobListResponse(
        items=[JobResponse.model_validate(j) for j in jobs],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a single job by ID."""
    query = select(Job).where(Job.id == job_id, Job.is_active == True)
    result = await db.execute(query)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobResponse.model_validate(job)


@router.post("", response_model=JobResponse, status_code=201)
async def create_job(
    job_data: JobCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new job listing."""
    job = Job(**job_data.model_dump())
    db.add(job)
    await db.commit()
    await db.refresh(job)

    return JobResponse.model_validate(job)


@router.patch("/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: int,
    job_data: JobUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a job listing."""
    query = select(Job).where(Job.id == job_id)
    result = await db.execute(query)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    update_data = job_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(job, field, value)

    await db.commit()
    await db.refresh(job)

    return JobResponse.model_validate(job)


@router.delete("/{job_id}", status_code=204)
async def delete_job(
    job_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Soft delete a job listing."""
    query = select(Job).where(Job.id == job_id)
    result = await db.execute(query)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job.is_active = False
    await db.commit()


@router.post("/collect", tags=["Collection"])
async def collect_jobs():
    """Collect AI job listings from curated sources."""
    collector = AIJobsCollector()

    try:
        # Collect jobs
        raw_data = await collector.collect()

        if not raw_data:
            return {"message": "No jobs collected", "collected": 0, "inserted": 0}

        # Transform data
        transformed_data = await collector.transform(raw_data)

        # Upsert into database
        async with AsyncSessionLocal() as session:
            inserted = 0
            updated = 0

            for item in transformed_data:
                # Check if exists
                db_query = select(Job).where(Job.external_id == item.get("external_id"))
                result = await session.execute(db_query)
                existing = result.scalar_one_or_none()

                if existing:
                    # Update existing
                    for key, value in item.items():
                        if hasattr(existing, key) and key != "id":
                            setattr(existing, key, value)
                    updated += 1
                else:
                    # Insert new
                    new_job = Job(**item)
                    session.add(new_job)
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
