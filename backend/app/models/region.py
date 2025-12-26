"""Region model for geographic content management."""
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from enum import Enum
from sqlalchemy import String, Text, Integer, Boolean, ForeignKey, Index, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from .base import TimestampMixin

if TYPE_CHECKING:
    from .admin import APISource


class RegionType(str, Enum):
    """Region type enum for hierarchical geographic structure."""
    GLOBAL = "global"
    CONTINENT = "continent"
    COUNTRY = "country"
    STATE = "state"
    CITY = "city"


class Region(Base, TimestampMixin):
    """Region model for hierarchical geographic content management.

    Supports a hierarchy like:
    - GLOBAL (e.g., "Global")
      - CONTINENT (e.g., "North America", "Europe", "Asia")
        - COUNTRY (e.g., "United States", "United Kingdom", "China")
          - STATE (e.g., "California", "New York")
            - CITY (e.g., "San Francisco", "New York City")
    """

    __tablename__ = "regions"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    region_type: Mapped[RegionType] = mapped_column(SQLEnum(RegionType), nullable=False)

    # Hierarchical relationship
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("regions.id", ondelete="SET NULL"))

    # ISO 3166 code for countries (e.g., "USA", "GBR", "CHN")
    iso_code: Mapped[Optional[str]] = mapped_column(String(3))

    # Default timezone for the region (e.g., "America/New_York")
    timezone: Mapped[Optional[str]] = mapped_column(String(50))

    # Optional description
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Status and ordering
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    parent: Mapped[Optional["Region"]] = relationship(
        "Region",
        remote_side=[id],
        back_populates="children",
        foreign_keys=[parent_id]
    )
    children: Mapped[List["Region"]] = relationship(
        "Region",
        back_populates="parent",
        foreign_keys=[parent_id],
        order_by="Region.sort_order, Region.name"
    )

    # Many-to-many relationship with APISource via association table
    sources: Mapped[List["APISource"]] = relationship(
        "APISource",
        secondary="api_source_regions",
        back_populates="regions"
    )

    __table_args__ = (
        Index("idx_regions_parent", "parent_id"),
        Index("idx_regions_type", "region_type"),
        Index("idx_regions_active", "is_active"),
    )

    def __repr__(self) -> str:
        return f"<Region {self.code}: {self.name} ({self.region_type.value})>"

    @property
    def full_path(self) -> str:
        """Return the full hierarchical path (e.g., 'Global > North America > United States')."""
        parts = [self.name]
        current = self.parent
        while current:
            parts.insert(0, current.name)
            current = current.parent
        return " > ".join(parts)
