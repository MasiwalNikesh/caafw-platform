"""Products API endpoints."""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.db.database import get_db, AsyncSessionLocal
from app.models.product import Product, ProductCategory
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductListResponse,
)
from app.collectors.product_hunt import ProductHuntCollector
from app.core.config import settings

router = APIRouter()


@router.get("", response_model=ProductListResponse)
async def list_products(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    category: Optional[str] = None,
    source: Optional[str] = None,
    pricing_type: Optional[str] = None,
    is_featured: Optional[bool] = None,
    search: Optional[str] = None,
    tag: Optional[str] = None,
    sort_by: str = Query(default="created_at", pattern="^(created_at|upvotes|name)$"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db),
):
    """List products with filtering and pagination."""
    query = select(Product).where(Product.is_active == True)

    # Apply filters
    if category:
        query = query.join(Product.categories).where(ProductCategory.slug == category)
    if source:
        query = query.where(Product.source == source)
    if pricing_type:
        query = query.where(Product.pricing_type == pricing_type)
    if is_featured is not None:
        query = query.where(Product.is_featured == is_featured)
    if tag:
        # Filter by tag in JSON array
        query = query.where(Product.tags.contains([tag]))
    if search:
        query = query.where(
            Product.name.ilike(f"%{search}%") |
            Product.tagline.ilike(f"%{search}%") |
            Product.description.ilike(f"%{search}%")
        )

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    # Apply sorting
    sort_column = getattr(Product, sort_by)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    query = query.options(selectinload(Product.categories))

    result = await db.execute(query)
    products = result.scalars().all()

    total_pages = (total + page_size - 1) // page_size

    return ProductListResponse(
        items=[ProductResponse.model_validate(p) for p in products],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )


@router.get("/categories", tags=["Categories"])
async def list_categories(
    db: AsyncSession = Depends(get_db),
):
    """List all product categories."""
    query = select(ProductCategory).order_by(ProductCategory.name)
    result = await db.execute(query)
    categories = result.scalars().all()

    return [
        {
            "id": cat.id,
            "name": cat.name,
            "slug": cat.slug,
            "description": cat.description,
            "icon": cat.icon,
        }
        for cat in categories
    ]


@router.get("/tags", tags=["Tags"])
async def list_popular_tags(
    limit: int = Query(default=20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """List popular tags from products."""
    # Get all products with tags
    query = select(Product.tags).where(Product.is_active == True, Product.tags.isnot(None))
    result = await db.execute(query)
    all_tags = result.scalars().all()

    # Count tag occurrences
    tag_counts: dict = {}
    for tags in all_tags:
        if tags:
            for tag in tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

    # Sort by count and return top tags
    sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:limit]

    return [{"name": tag, "count": count} for tag, count in sorted_tags]


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a single product by ID."""
    query = (
        select(Product)
        .where(Product.id == product_id, Product.is_active == True)
        .options(selectinload(Product.categories))
    )
    result = await db.execute(query)
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return ProductResponse.model_validate(product)


@router.get("/slug/{slug}", response_model=ProductResponse)
async def get_product_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a single product by slug."""
    query = (
        select(Product)
        .where(Product.slug == slug, Product.is_active == True)
        .options(selectinload(Product.categories))
    )
    result = await db.execute(query)
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return ProductResponse.model_validate(product)


@router.post("", response_model=ProductResponse, status_code=201)
async def create_product(
    product_data: ProductCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new product."""
    # Check if slug exists
    existing = await db.execute(
        select(Product).where(Product.slug == product_data.slug)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Product with this slug already exists")

    product = Product(**product_data.model_dump(exclude={"category_ids"}))
    db.add(product)
    await db.commit()
    await db.refresh(product)

    return ProductResponse.model_validate(product)


@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a product."""
    query = select(Product).where(Product.id == product_id)
    result = await db.execute(query)
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    update_data = product_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    await db.commit()
    await db.refresh(product)

    return ProductResponse.model_validate(product)


@router.delete("/{product_id}", status_code=204)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Soft delete a product."""
    query = select(Product).where(Product.id == product_id)
    result = await db.execute(query)
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product.is_active = False
    await db.commit()


@router.post("/collect", tags=["Collection"])
async def collect_products_from_producthunt():
    """Manually trigger Product Hunt data collection."""
    import httpx
    import re
    from datetime import datetime

    # Use configured token from settings
    token = settings.PRODUCT_HUNT_TOKEN
    if not token:
        raise HTTPException(status_code=500, detail="PRODUCT_HUNT_TOKEN not configured")

    graphql_query = """
    query GetProducts($first: Int!) {
        posts(first: $first) {
            edges {
                node {
                    id
                    name
                    tagline
                    description
                    url
                    website
                    votesCount
                    commentsCount
                    createdAt
                    featuredAt
                    thumbnail {
                        url
                    }
                    topics {
                        edges {
                            node {
                                name
                                slug
                            }
                        }
                    }
                }
            }
        }
    }
    """

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.producthunt.com/v2/api/graphql",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                json={"query": graphql_query, "variables": {"first": 20}},
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()

        # Check for API errors
        if "errors" in data:
            raise HTTPException(status_code=400, detail=f"Product Hunt API error: {data['errors']}")

        edges = data.get("data", {}).get("posts", {}).get("edges", [])
        raw_data = [edge["node"] for edge in edges]

        # Transform data inline
        def create_slug(name: str) -> str:
            slug = name.lower()
            slug = re.sub(r"[^a-z0-9\s-]", "", slug)
            slug = re.sub(r"[\s_]+", "-", slug)
            slug = re.sub(r"-+", "-", slug)
            return slug.strip("-")

        def parse_date(date_str):
            if not date_str:
                return None
            try:
                dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                # Convert to naive datetime for database compatibility
                return dt.replace(tzinfo=None)
            except ValueError:
                return None

        # Topic to category mapping
        topic_to_category = {
            "artificial-intelligence": "ai-ml",
            "machine-learning": "ai-ml",
            "generative-ai": "ai-ml",
            "ai": "ai-ml",
            "developer-tools": "developer-tools",
            "developer": "developer-tools",
            "no-code": "developer-tools",
            "productivity": "productivity",
            "automation": "productivity",
            "design": "design",
            "design-tools": "design",
            "marketing": "marketing",
            "analytics": "analytics",
            "writing": "writing",
        }

        transformed_data = []
        for item in raw_data:
            topics = item.get("topics", {}).get("edges", [])
            tags = [t["node"]["name"] for t in topics]
            topic_slugs = [t["node"]["slug"] for t in topics]

            # Map topics to category slugs
            category_slugs = set()
            for topic_slug in topic_slugs:
                if topic_slug in topic_to_category:
                    category_slugs.add(topic_to_category[topic_slug])

            product = {
                "external_id": str(item.get("id")),
                "source": "product_hunt",
                "name": item.get("name"),
                "slug": create_slug(item.get("name", "")),
                "tagline": item.get("tagline"),
                "description": item.get("description"),
                "website_url": item.get("website") or item.get("url"),
                "thumbnail_url": item.get("thumbnail", {}).get("url") if item.get("thumbnail") else None,
                "upvotes": item.get("votesCount", 0),
                "comments_count": item.get("commentsCount", 0),
                "tags": tags,
                "launched_at": parse_date(item.get("createdAt")),
                "is_featured": item.get("featuredAt") is not None,
                "_category_slugs": list(category_slugs),
            }
            transformed_data.append(product)

        if not transformed_data:
            return {"message": "No products collected", "collected": 0, "inserted": 0}

        # Upsert into database
        async with AsyncSessionLocal() as session:
            inserted = 0
            updated = 0
            categories_assigned = 0

            # Pre-fetch all categories
            cat_query = select(ProductCategory)
            cat_result = await session.execute(cat_query)
            all_categories = {cat.slug: cat for cat in cat_result.scalars().all()}

            for item in transformed_data:
                # Extract category slugs before passing to Product model
                category_slugs = item.pop("_category_slugs", [])

                # Check if exists (load categories for relationship check)
                db_query = (
                    select(Product)
                    .where(Product.external_id == item.get("external_id"))
                    .options(selectinload(Product.categories))
                )
                result = await session.execute(db_query)
                existing = result.scalar_one_or_none()

                if existing:
                    # Update existing product
                    for key, value in item.items():
                        if hasattr(existing, key) and key != "id":
                            setattr(existing, key, value)
                    product_obj = existing
                    updated += 1
                else:
                    # Insert new product
                    new_product = Product(**item)
                    session.add(new_product)
                    await session.flush()  # Get the ID
                    product_obj = new_product
                    inserted += 1

                # Assign categories
                if category_slugs:
                    for cat_slug in category_slugs:
                        if cat_slug in all_categories:
                            cat = all_categories[cat_slug]
                            if cat not in product_obj.categories:
                                product_obj.categories.append(cat)
                                categories_assigned += 1

            await session.commit()

        return {
            "message": "Collection complete",
            "collected": len(transformed_data),
            "inserted": inserted,
            "updated": updated,
            "categories_assigned": categories_assigned,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Collection failed: {str(e)}")
