"""Investments and companies API endpoints."""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.db.database import get_db, AsyncSessionLocal
from app.models.investment import Company, FundingRound
from app.schemas.investment import CompanyResponse, CompanyListResponse, FundingRoundResponse
from app.collectors.ai_investments import AIInvestmentsCollector

router = APIRouter()


@router.get("/companies", response_model=CompanyListResponse)
async def list_companies(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    funding_status: Optional[str] = None,
    country: Optional[str] = None,
    founded_year_min: Optional[int] = None,
    founded_year_max: Optional[int] = None,
    total_funding_min: Optional[int] = None,
    is_featured: Optional[bool] = None,
    search: Optional[str] = None,
    sort_by: str = Query(default="total_funding", pattern="^(total_funding|founded_year|created_at|last_funding_date)$"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db),
):
    """List companies with filtering and pagination."""
    query = select(Company).where(
        Company.is_active == True,
        Company.is_ai_company == True,
    )

    # Apply filters
    if funding_status:
        query = query.where(Company.funding_status == funding_status)
    if country:
        query = query.where(Company.country.ilike(f"%{country}%"))
    if founded_year_min:
        query = query.where(Company.founded_year >= founded_year_min)
    if founded_year_max:
        query = query.where(Company.founded_year <= founded_year_max)
    if total_funding_min:
        query = query.where(Company.total_funding >= total_funding_min)
    if is_featured is not None:
        query = query.where(Company.is_featured == is_featured)
    if search:
        query = query.where(
            Company.name.ilike(f"%{search}%") |
            Company.description.ilike(f"%{search}%")
        )

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    # Apply sorting
    sort_column = getattr(Company, sort_by)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc().nullslast())
    else:
        query = query.order_by(sort_column.asc().nullsfirst())

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    query = query.options(selectinload(Company.funding_rounds))

    result = await db.execute(query)
    companies = result.scalars().all()

    total_pages = (total + page_size - 1) // page_size

    return CompanyListResponse(
        items=[CompanyResponse.model_validate(c) for c in companies],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )


@router.get("/companies/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a single company by ID."""
    query = (
        select(Company)
        .where(Company.id == company_id, Company.is_active == True)
        .options(selectinload(Company.funding_rounds))
    )
    result = await db.execute(query)
    company = result.scalar_one_or_none()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    return CompanyResponse.model_validate(company)


@router.get("/companies/slug/{slug}", response_model=CompanyResponse)
async def get_company_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a company by slug."""
    query = (
        select(Company)
        .where(Company.slug == slug, Company.is_active == True)
        .options(selectinload(Company.funding_rounds))
    )
    result = await db.execute(query)
    company = result.scalar_one_or_none()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    return CompanyResponse.model_validate(company)


@router.get("/funding-rounds", response_model=List[FundingRoundResponse])
async def list_funding_rounds(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    round_type: Optional[str] = None,
    min_amount: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    """List recent funding rounds."""
    query = select(FundingRound)

    if round_type:
        query = query.where(FundingRound.round_type == round_type)
    if min_amount:
        query = query.where(FundingRound.amount >= min_amount)

    query = query.order_by(FundingRound.announced_at.desc().nullslast())

    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    rounds = result.scalars().all()

    return [FundingRoundResponse.model_validate(r) for r in rounds]


@router.post("/collect", tags=["Collection"])
async def collect_investments():
    """Collect AI company investment and funding data."""
    collector = AIInvestmentsCollector()

    try:
        # Collect data
        raw_data = await collector.collect()

        if not raw_data:
            return {"message": "No data collected", "companies": 0, "funding_rounds": 0}

        # Transform data
        companies_data, funding_rounds_data = await collector.transform(raw_data)

        # Upsert into database
        async with AsyncSessionLocal() as session:
            companies_inserted = 0
            companies_updated = 0
            rounds_inserted = 0

            # First, insert/update companies
            company_id_map = {}
            for item in companies_data:
                db_query = select(Company).where(Company.external_id == item.get("external_id"))
                result = await session.execute(db_query)
                existing = result.scalar_one_or_none()

                if existing:
                    for key, value in item.items():
                        if hasattr(existing, key) and key != "id":
                            setattr(existing, key, value)
                    companies_updated += 1
                    company_id_map[item["slug"]] = existing.id
                else:
                    new_company = Company(**item)
                    session.add(new_company)
                    await session.flush()
                    companies_inserted += 1
                    company_id_map[item["slug"]] = new_company.id

            # Then, insert funding rounds
            for round_item in funding_rounds_data:
                company_slug = round_item.pop("_company_slug", None)
                if company_slug and company_slug in company_id_map:
                    round_item["company_id"] = company_id_map[company_slug]

                    db_query = select(FundingRound).where(
                        FundingRound.external_id == round_item.get("external_id")
                    )
                    result = await session.execute(db_query)
                    existing_round = result.scalar_one_or_none()

                    if not existing_round:
                        new_round = FundingRound(**round_item)
                        session.add(new_round)
                        rounds_inserted += 1

            await session.commit()

        return {
            "message": "Collection complete",
            "companies_inserted": companies_inserted,
            "companies_updated": companies_updated,
            "funding_rounds_inserted": rounds_inserted,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Collection failed: {str(e)}")
