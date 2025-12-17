"""Investment and company models."""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Text, Integer, BigInteger, Float, Boolean, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from .base import TimestampMixin


class Company(Base, TimestampMixin):
    """Company model for tracking AI startups and companies."""

    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True)
    external_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True)
    source: Mapped[str] = mapped_column(String(50), nullable=False)  # crunchbase, tracxn, etc.

    # Basic Info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(300), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    short_description: Mapped[Optional[str]] = mapped_column(String(500))

    # URLs
    website_url: Mapped[Optional[str]] = mapped_column(String(500))
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(500))
    twitter_url: Mapped[Optional[str]] = mapped_column(String(500))
    crunchbase_url: Mapped[Optional[str]] = mapped_column(String(500))
    logo_url: Mapped[Optional[str]] = mapped_column(String(500))

    # Location
    headquarters: Mapped[Optional[str]] = mapped_column(String(255))
    city: Mapped[Optional[str]] = mapped_column(String(100))
    state: Mapped[Optional[str]] = mapped_column(String(100))
    country: Mapped[Optional[str]] = mapped_column(String(100))

    # Company Details
    founded_year: Mapped[Optional[int]] = mapped_column(Integer)
    employee_count: Mapped[Optional[str]] = mapped_column(String(50))  # "11-50", "51-100", etc.
    company_type: Mapped[Optional[str]] = mapped_column(String(50))  # startup, public, private

    # Industry
    industries: Mapped[Optional[List[str]]] = mapped_column(JSON)
    categories: Mapped[Optional[List[str]]] = mapped_column(JSON)

    # Funding
    total_funding: Mapped[Optional[int]] = mapped_column(BigInteger)
    funding_currency: Mapped[Optional[str]] = mapped_column(String(10), default="USD")
    last_funding_type: Mapped[Optional[str]] = mapped_column(String(50))
    last_funding_date: Mapped[Optional[datetime]] = mapped_column()
    funding_status: Mapped[Optional[str]] = mapped_column(String(50))  # seed, series_a, etc.
    ipo_status: Mapped[Optional[str]] = mapped_column(String(50))  # private, public

    # Valuation
    valuation: Mapped[Optional[int]] = mapped_column(BigInteger)
    valuation_date: Mapped[Optional[datetime]] = mapped_column()

    # Investors
    num_investors: Mapped[int] = mapped_column(Integer, default=0)
    lead_investors: Mapped[Optional[List[str]]] = mapped_column(JSON)

    # Status
    is_ai_company: Mapped[bool] = mapped_column(Boolean, default=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Extra data
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON)

    # Relationships
    funding_rounds: Mapped[List["FundingRound"]] = relationship(back_populates="company")

    def __repr__(self) -> str:
        return f"<Company {self.name}>"


class FundingRound(Base, TimestampMixin):
    """Funding round model."""

    __tablename__ = "funding_rounds"

    id: Mapped[int] = mapped_column(primary_key=True)
    external_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)

    # Round Info
    round_type: Mapped[str] = mapped_column(String(50), nullable=False)  # seed, series_a, etc.
    round_number: Mapped[Optional[int]] = mapped_column(Integer)

    # Amount
    amount: Mapped[Optional[int]] = mapped_column(BigInteger)
    currency: Mapped[Optional[str]] = mapped_column(String(10), default="USD")

    # Valuation
    pre_money_valuation: Mapped[Optional[int]] = mapped_column(BigInteger)
    post_money_valuation: Mapped[Optional[int]] = mapped_column(BigInteger)

    # Investors
    lead_investors: Mapped[Optional[List[str]]] = mapped_column(JSON)
    investors: Mapped[Optional[List[str]]] = mapped_column(JSON)
    num_investors: Mapped[int] = mapped_column(Integer, default=0)

    # Source
    source_url: Mapped[Optional[str]] = mapped_column(String(500))

    # Dates
    announced_at: Mapped[Optional[datetime]] = mapped_column()
    closed_at: Mapped[Optional[datetime]] = mapped_column()

    # Extra data
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON)

    # Relationships
    company: Mapped[Company] = relationship(back_populates="funding_rounds")

    def __repr__(self) -> str:
        return f"<FundingRound {self.round_type} for {self.company_id}>"
