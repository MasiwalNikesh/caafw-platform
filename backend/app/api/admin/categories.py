"""Admin categories management API endpoints."""
import re
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from sqlalchemy.orm import selectinload

from app.db.database import get_db
from app.models.user import User
from app.models.admin import ContentCategory, ContentCategoryAssignment, AuditLog
from app.core.deps import get_current_moderator, get_current_admin
from app.schemas.admin import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryTreeResponse,
)

router = APIRouter()


def create_slug(name: str) -> str:
    """Create URL-friendly slug from name."""
    slug = name.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")[:100]


async def log_audit(
    db: AsyncSession,
    admin_id: int,
    action: str,
    entity_type: str,
    entity_id: int,
    old_values: dict = None,
    new_values: dict = None,
    request: Request = None,
):
    """Log an admin action."""
    ip_address = None
    user_agent = None
    if request:
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

    audit_log = AuditLog(
        admin_id=admin_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        old_values=old_values,
        new_values=new_values,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.add(audit_log)
    await db.flush()


def build_category_tree(categories: List[ContentCategory], parent_id: int = None) -> List[CategoryResponse]:
    """Build hierarchical category tree."""
    tree = []
    for category in categories:
        if category.parent_id == parent_id:
            children = build_category_tree(categories, category.id)
            cat_response = CategoryResponse(
                id=category.id,
                name=category.name,
                slug=category.slug,
                description=category.description,
                parent_id=category.parent_id,
                icon=category.icon,
                color=category.color,
                sort_order=category.sort_order,
                is_active=category.is_active,
                created_at=category.created_at,
                updated_at=category.updated_at,
                children=children,
            )
            tree.append(cat_response)
    return sorted(tree, key=lambda x: x.sort_order)


@router.get("", response_model=CategoryTreeResponse)
async def list_categories(
    flat: bool = Query(False, description="Return flat list instead of tree"),
    include_inactive: bool = False,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_moderator),
):
    """List all categories as a tree or flat list."""
    query = select(ContentCategory)
    if not include_inactive:
        query = query.where(ContentCategory.is_active == True)
    query = query.order_by(ContentCategory.sort_order, ContentCategory.name)

    result = await db.execute(query)
    categories = list(result.scalars())

    if flat:
        return CategoryTreeResponse(
            categories=[
                CategoryResponse(
                    id=c.id,
                    name=c.name,
                    slug=c.slug,
                    description=c.description,
                    parent_id=c.parent_id,
                    icon=c.icon,
                    color=c.color,
                    sort_order=c.sort_order,
                    is_active=c.is_active,
                    created_at=c.created_at,
                    updated_at=c.updated_at,
                    children=[],
                )
                for c in categories
            ]
        )

    tree = build_category_tree(categories)
    return CategoryTreeResponse(categories=tree)


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_moderator),
):
    """Get a specific category with its children."""
    category = await db.get(ContentCategory, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    # Get all categories to build children
    query = select(ContentCategory).order_by(ContentCategory.sort_order)
    result = await db.execute(query)
    all_categories = list(result.scalars())

    children = build_category_tree(all_categories, category_id)

    return CategoryResponse(
        id=category.id,
        name=category.name,
        slug=category.slug,
        description=category.description,
        parent_id=category.parent_id,
        icon=category.icon,
        color=category.color,
        sort_order=category.sort_order,
        is_active=category.is_active,
        created_at=category.created_at,
        updated_at=category.updated_at,
        children=children,
    )


@router.post("", response_model=CategoryResponse)
async def create_category(
    category_data: CategoryCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Create a new category."""
    # Check if name already exists
    existing = await db.scalar(
        select(ContentCategory).where(ContentCategory.name == category_data.name)
    )
    if existing:
        raise HTTPException(status_code=400, detail="Category with this name already exists")

    # Validate parent exists if specified
    if category_data.parent_id:
        parent = await db.get(ContentCategory, category_data.parent_id)
        if not parent:
            raise HTTPException(status_code=400, detail="Parent category not found")

    # Create slug
    slug = create_slug(category_data.name)
    slug_exists = await db.scalar(select(ContentCategory).where(ContentCategory.slug == slug))
    if slug_exists:
        count = await db.scalar(select(func.count(ContentCategory.id)).where(ContentCategory.slug.like(f"{slug}%")))
        slug = f"{slug}-{count + 1}"

    category = ContentCategory(
        name=category_data.name,
        slug=slug,
        description=category_data.description,
        parent_id=category_data.parent_id,
        icon=category_data.icon,
        color=category_data.color,
        sort_order=category_data.sort_order,
        is_active=category_data.is_active,
    )
    db.add(category)
    await db.flush()

    await log_audit(
        db=db,
        admin_id=admin.id,
        action="create_category",
        entity_type="category",
        entity_id=category.id,
        new_values={"name": category.name, "slug": category.slug},
        request=request,
    )

    await db.commit()
    await db.refresh(category)

    return CategoryResponse(
        id=category.id,
        name=category.name,
        slug=category.slug,
        description=category.description,
        parent_id=category.parent_id,
        icon=category.icon,
        color=category.color,
        sort_order=category.sort_order,
        is_active=category.is_active,
        created_at=category.created_at,
        updated_at=category.updated_at,
        children=[],
    )


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Update a category."""
    category = await db.get(ContentCategory, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    old_values = {
        "name": category.name,
        "parent_id": category.parent_id,
        "sort_order": category.sort_order,
    }

    # Check name uniqueness if changing
    if category_data.name and category_data.name != category.name:
        existing = await db.scalar(
            select(ContentCategory).where(ContentCategory.name == category_data.name)
        )
        if existing:
            raise HTTPException(status_code=400, detail="Category with this name already exists")
        category.name = category_data.name
        category.slug = create_slug(category_data.name)

    # Validate parent if changing
    if category_data.parent_id is not None:
        if category_data.parent_id == category_id:
            raise HTTPException(status_code=400, detail="Category cannot be its own parent")
        if category_data.parent_id:
            parent = await db.get(ContentCategory, category_data.parent_id)
            if not parent:
                raise HTTPException(status_code=400, detail="Parent category not found")
        category.parent_id = category_data.parent_id

    if category_data.description is not None:
        category.description = category_data.description
    if category_data.icon is not None:
        category.icon = category_data.icon
    if category_data.color is not None:
        category.color = category_data.color
    if category_data.sort_order is not None:
        category.sort_order = category_data.sort_order
    if category_data.is_active is not None:
        category.is_active = category_data.is_active

    await log_audit(
        db=db,
        admin_id=admin.id,
        action="update_category",
        entity_type="category",
        entity_id=category_id,
        old_values=old_values,
        new_values={"name": category.name, "parent_id": category.parent_id},
        request=request,
    )

    await db.commit()
    await db.refresh(category)

    return CategoryResponse(
        id=category.id,
        name=category.name,
        slug=category.slug,
        description=category.description,
        parent_id=category.parent_id,
        icon=category.icon,
        color=category.color,
        sort_order=category.sort_order,
        is_active=category.is_active,
        created_at=category.created_at,
        updated_at=category.updated_at,
        children=[],
    )


@router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    request: Request,
    reassign_to: Optional[int] = Query(None, description="Category ID to reassign content to"),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Delete a category. Optionally reassign content to another category."""
    category = await db.get(ContentCategory, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    # Check for children
    children_count = await db.scalar(
        select(func.count(ContentCategory.id)).where(ContentCategory.parent_id == category_id)
    )
    if children_count > 0:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete category with children. Delete or reassign children first."
        )

    category_name = category.name

    # Handle content reassignment
    if reassign_to:
        target = await db.get(ContentCategory, reassign_to)
        if not target:
            raise HTTPException(status_code=400, detail="Target category not found")

        # Update assignments
        await db.execute(
            ContentCategoryAssignment.__table__.update()
            .where(ContentCategoryAssignment.category_id == category_id)
            .values(category_id=reassign_to)
        )
    else:
        # Delete assignments
        await db.execute(
            delete(ContentCategoryAssignment).where(ContentCategoryAssignment.category_id == category_id)
        )

    await db.delete(category)

    await log_audit(
        db=db,
        admin_id=admin.id,
        action="delete_category",
        entity_type="category",
        entity_id=category_id,
        old_values={"name": category_name},
        new_values={"reassigned_to": reassign_to} if reassign_to else None,
        request=request,
    )

    await db.commit()
    return {"message": "Category deleted", "id": category_id}


@router.patch("/{category_id}/reorder")
async def reorder_category(
    category_id: int,
    new_order: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Change the sort order of a category."""
    category = await db.get(ContentCategory, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    old_order = category.sort_order
    category.sort_order = new_order

    await log_audit(
        db=db,
        admin_id=admin.id,
        action="reorder_category",
        entity_type="category",
        entity_id=category_id,
        old_values={"sort_order": old_order},
        new_values={"sort_order": new_order},
        request=request,
    )

    await db.commit()
    return {"message": "Category reordered", "id": category_id, "sort_order": new_order}


@router.post("/{category_id}/assign")
async def assign_content_to_category(
    category_id: int,
    content_type: str,
    content_ids: List[int],
    is_primary: bool = False,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_moderator),
):
    """Assign content items to a category."""
    category = await db.get(ContentCategory, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    assigned = []
    for content_id in content_ids:
        # Check if already assigned
        existing = await db.scalar(
            select(ContentCategoryAssignment.id).where(
                ContentCategoryAssignment.category_id == category_id,
                ContentCategoryAssignment.content_type == content_type,
                ContentCategoryAssignment.content_id == content_id,
            )
        )
        if existing:
            continue

        # If setting as primary, unset other primary assignments
        if is_primary:
            await db.execute(
                ContentCategoryAssignment.__table__.update()
                .where(
                    ContentCategoryAssignment.content_type == content_type,
                    ContentCategoryAssignment.content_id == content_id,
                    ContentCategoryAssignment.is_primary == True,
                )
                .values(is_primary=False)
            )

        assignment = ContentCategoryAssignment(
            category_id=category_id,
            content_type=content_type,
            content_id=content_id,
            is_primary=is_primary,
        )
        db.add(assignment)
        assigned.append(content_id)

    if assigned and request:
        await log_audit(
            db=db,
            admin_id=admin.id,
            action="assign_category",
            entity_type=content_type,
            entity_id=None,
            new_values={"category": category.name, "content_ids": assigned},
            request=request,
        )

    await db.commit()
    return {"message": "Content assigned to category", "assigned": assigned}


@router.delete("/{category_id}/assign/{content_type}/{content_id}")
async def remove_content_from_category(
    category_id: int,
    content_type: str,
    content_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_moderator),
):
    """Remove a content item from a category."""
    assignment = await db.scalar(
        select(ContentCategoryAssignment).where(
            ContentCategoryAssignment.category_id == category_id,
            ContentCategoryAssignment.content_type == content_type,
            ContentCategoryAssignment.content_id == content_id,
        )
    )
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    await db.delete(assignment)

    await log_audit(
        db=db,
        admin_id=admin.id,
        action="remove_category",
        entity_type=content_type,
        entity_id=content_id,
        old_values={"category_id": category_id},
        request=request,
    )

    await db.commit()
    return {"message": "Content removed from category"}
