"""Research paper models."""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Text, Integer, Boolean, JSON, ForeignKey, Table, Column, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from .base import TimestampMixin
from .admin import ContentStatus


# Association table for paper-author many-to-many
paper_authors = Table(
    "paper_authors",
    Base.metadata,
    Column("paper_id", Integer, ForeignKey("research_papers.id"), primary_key=True),
    Column("author_id", Integer, ForeignKey("paper_authors_table.id"), primary_key=True),
)


class PaperAuthor(Base, TimestampMixin):
    """Research paper author model."""

    __tablename__ = "paper_authors_table"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    affiliation: Mapped[Optional[str]] = mapped_column(String(255))
    email: Mapped[Optional[str]] = mapped_column(String(255))
    orcid: Mapped[Optional[str]] = mapped_column(String(50))
    semantic_scholar_id: Mapped[Optional[str]] = mapped_column(String(100))

    # Relationships
    papers: Mapped[List["ResearchPaper"]] = relationship(
        secondary=paper_authors, back_populates="authors"
    )


class ResearchPaper(Base, TimestampMixin):
    """Research paper model."""

    __tablename__ = "research_papers"

    id: Mapped[int] = mapped_column(primary_key=True)
    external_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True)
    source: Mapped[str] = mapped_column(String(50), nullable=False)  # arxiv, papers_with_code, semantic_scholar

    # Basic Info
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    slug: Mapped[str] = mapped_column(String(550), nullable=False)
    abstract: Mapped[Optional[str]] = mapped_column(Text)

    # IDs
    arxiv_id: Mapped[Optional[str]] = mapped_column(String(50))
    doi: Mapped[Optional[str]] = mapped_column(String(100))

    # URLs
    pdf_url: Mapped[Optional[str]] = mapped_column(String(500))
    paper_url: Mapped[str] = mapped_column(String(500), nullable=False)
    code_url: Mapped[Optional[str]] = mapped_column(String(500))

    # Categories
    primary_category: Mapped[Optional[str]] = mapped_column(String(50))
    categories: Mapped[Optional[List[str]]] = mapped_column(JSON)

    # Metrics
    citations: Mapped[int] = mapped_column(Integer, default=0)
    stars: Mapped[int] = mapped_column(Integer, default=0)  # For papers with code repos

    # Tasks and methods (from Papers With Code)
    tasks: Mapped[Optional[List[str]]] = mapped_column(JSON)
    methods: Mapped[Optional[List[str]]] = mapped_column(JSON)
    datasets: Mapped[Optional[List[str]]] = mapped_column(JSON)

    # Status
    has_code: Mapped[bool] = mapped_column(Boolean, default=False)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)

    # Moderation status (default APPROVED for arXiv - trusted source)
    moderation_status: Mapped[ContentStatus] = mapped_column(
        SQLEnum(ContentStatus, values_callable=lambda x: [e.value for e in x]),
        default=ContentStatus.APPROVED,
        nullable=False,
        index=True
    )
    reviewed_by_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    reviewed_at: Mapped[Optional[datetime]] = mapped_column()
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text)

    # Dates
    published_at: Mapped[Optional[datetime]] = mapped_column()
    updated_at_source: Mapped[Optional[datetime]] = mapped_column()

    # Extra data
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON)

    # Region (optional - for regional content filtering)
    region_id: Mapped[Optional[int]] = mapped_column(ForeignKey("regions.id", ondelete="SET NULL"))

    # Relationships
    authors: Mapped[List[PaperAuthor]] = relationship(
        secondary=paper_authors, back_populates="papers"
    )

    def __repr__(self) -> str:
        return f"<ResearchPaper {self.title[:50]}...>"
