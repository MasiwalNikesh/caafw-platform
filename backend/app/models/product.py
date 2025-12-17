"""Product and AI Tools models."""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Text, Integer, Float, Boolean, ForeignKey, Table, Column, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from .base import TimestampMixin


# Association table for product-category many-to-many
product_categories = Table(
    "product_categories",
    Base.metadata,
    Column("product_id", Integer, ForeignKey("products.id"), primary_key=True),
    Column("category_id", Integer, ForeignKey("categories.id"), primary_key=True),
)


class ProductCategory(Base, TimestampMixin):
    """Category for AI products/tools."""

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    icon: Mapped[Optional[str]] = mapped_column(String(50))
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("categories.id"))

    # Relationships
    products: Mapped[List["Product"]] = relationship(
        secondary=product_categories, back_populates="categories"
    )
    children: Mapped[List["ProductCategory"]] = relationship("ProductCategory")


class Product(Base, TimestampMixin):
    """AI Product/Tool model."""

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    external_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True)
    source: Mapped[str] = mapped_column(String(50), nullable=False)  # product_hunt, futurtools, etc.

    # Basic Info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    tagline: Mapped[Optional[str]] = mapped_column(String(500))
    description: Mapped[Optional[str]] = mapped_column(Text)

    # URLs
    website_url: Mapped[Optional[str]] = mapped_column(String(500))
    logo_url: Mapped[Optional[str]] = mapped_column(String(500))
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(500))

    # Metrics
    upvotes: Mapped[int] = mapped_column(Integer, default=0)
    comments_count: Mapped[int] = mapped_column(Integer, default=0)
    rating: Mapped[Optional[float]] = mapped_column(Float)
    reviews_count: Mapped[int] = mapped_column(Integer, default=0)

    # Pricing
    pricing_type: Mapped[Optional[str]] = mapped_column(String(50))  # free, freemium, paid
    pricing_details: Mapped[Optional[dict]] = mapped_column(JSON)

    # Status
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Dates
    launched_at: Mapped[Optional[datetime]] = mapped_column()

    # SEO
    meta_title: Mapped[Optional[str]] = mapped_column(String(255))
    meta_description: Mapped[Optional[str]] = mapped_column(String(500))

    # Tags and extra data
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON)
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON)

    # Relationships
    categories: Mapped[List[ProductCategory]] = relationship(
        secondary=product_categories, back_populates="products"
    )

    def __repr__(self) -> str:
        return f"<Product {self.name}>"
