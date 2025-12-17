"""Investment and company schemas."""
from datetime import datetime
from typing import Optional, List
from .common import BaseResponse, PaginatedResponse


class FundingRoundResponse(BaseResponse):
    """Funding round response schema."""

    id: int
    round_type: str
    round_number: Optional[int] = None
    amount: Optional[int] = None
    currency: str = "USD"
    pre_money_valuation: Optional[int] = None
    post_money_valuation: Optional[int] = None
    lead_investors: Optional[List[str]] = None
    investors: Optional[List[str]] = None
    num_investors: int = 0
    announced_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None


class CompanyResponse(BaseResponse):
    """Company response schema."""

    id: int
    name: str
    slug: str
    description: Optional[str] = None
    short_description: Optional[str] = None
    source: str
    website_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    twitter_url: Optional[str] = None
    crunchbase_url: Optional[str] = None
    logo_url: Optional[str] = None
    headquarters: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    founded_year: Optional[int] = None
    employee_count: Optional[str] = None
    company_type: Optional[str] = None
    industries: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    total_funding: Optional[int] = None
    funding_currency: str = "USD"
    last_funding_type: Optional[str] = None
    last_funding_date: Optional[datetime] = None
    funding_status: Optional[str] = None
    ipo_status: Optional[str] = None
    valuation: Optional[int] = None
    valuation_date: Optional[datetime] = None
    num_investors: int = 0
    lead_investors: Optional[List[str]] = None
    is_ai_company: bool = True
    is_featured: bool = False
    funding_rounds: List[FundingRoundResponse] = []
    created_at: datetime
    updated_at: datetime


class CompanyListResponse(PaginatedResponse[CompanyResponse]):
    """Paginated company list response."""

    pass
