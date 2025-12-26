"""Bookmark and Collection API endpoints."""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.deps import get_db, get_current_user
from app.models import (
    User,
    Bookmark,
    Collection,
    CollectionItem,
    Product,
    Job,
    ResearchPaper,
    LearningResource,
    LearningPath,
    Event,
    MCPServer,
    NewsArticle,
    HackerNewsItem,
    GitHubRepo,
)
from app.schemas.bookmark import (
    BookmarkCreate,
    BookmarkUpdate,
    BookmarkResponse,
    BookmarkListResponse,
    CollectionCreate,
    CollectionUpdate,
    CollectionResponse,
    CollectionDetailResponse,
    CollectionListResponse,
    AddToCollectionRequest,
    ReorderCollectionItemsRequest,
    ContentType,
)

router = APIRouter()


# Content type to model mapping
CONTENT_MODELS = {
    ContentType.PRODUCT: Product,
    ContentType.JOB: Job,
    ContentType.RESEARCH: ResearchPaper,
    ContentType.LEARNING: LearningResource,
    ContentType.LEARNING_PATH: LearningPath,
    ContentType.EVENT: Event,
    ContentType.MCP_SERVER: MCPServer,
    ContentType.NEWS: NewsArticle,
    ContentType.HACKERNEWS: HackerNewsItem,
    ContentType.GITHUB: GitHubRepo,
}


async def get_content_data(db: AsyncSession, content_type: str, content_id: int) -> Optional[dict]:
    """Fetch content data for a bookmark."""
    model = CONTENT_MODELS.get(ContentType(content_type))
    if not model:
        return None
    
    result = await db.execute(select(model).where(model.id == content_id))
    item = result.scalar_one_or_none()
    if not item:
        return None
    
    # Return basic info based on content type
    data = {"id": item.id}
    
    if hasattr(item, "name"):
        data["name"] = item.name
    if hasattr(item, "title"):
        data["title"] = item.title
    if hasattr(item, "description"):
        data["description"] = item.description[:200] if item.description else None
    if hasattr(item, "url"):
        data["url"] = item.url
    if hasattr(item, "logo_url"):
        data["logo_url"] = item.logo_url
    if hasattr(item, "company_logo"):
        data["logo_url"] = item.company_logo
    if hasattr(item, "company_name"):
        data["company_name"] = item.company_name
    
    return data


# ============ Bookmark Endpoints ============

@router.post("/bookmarks", response_model=BookmarkResponse, status_code=201)
async def create_bookmark(
    bookmark: BookmarkCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new bookmark."""
    # Check if bookmark already exists
    existing = await db.execute(
        select(Bookmark).where(
            Bookmark.user_id == current_user.id,
            Bookmark.content_type == bookmark.content_type.value,
            Bookmark.content_id == bookmark.content_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Bookmark already exists")
    
    # Verify content exists
    content_data = await get_content_data(db, bookmark.content_type.value, bookmark.content_id)
    if not content_data:
        raise HTTPException(status_code=404, detail="Content not found")
    
    db_bookmark = Bookmark(
        user_id=current_user.id,
        content_type=bookmark.content_type.value,
        content_id=bookmark.content_id,
        notes=bookmark.notes,
    )
    db.add(db_bookmark)
    await db.commit()
    await db.refresh(db_bookmark)
    
    return BookmarkResponse(
        **{k: v for k, v in db_bookmark.__dict__.items() if not k.startswith("_")},
        content_data=content_data,
    )


@router.get("/bookmarks", response_model=BookmarkListResponse)
async def list_bookmarks(
    content_type: Optional[ContentType] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List user's bookmarks with optional filtering."""
    query = select(Bookmark).where(Bookmark.user_id == current_user.id)
    
    if content_type:
        query = query.where(Bookmark.content_type == content_type.value)
    
    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Paginate
    query = query.order_by(Bookmark.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    bookmarks = result.scalars().all()
    
    # Fetch content data for each bookmark
    items = []
    for bookmark in bookmarks:
        content_data = await get_content_data(db, bookmark.content_type, bookmark.content_id)
        items.append(BookmarkResponse(
            **{k: v for k, v in bookmark.__dict__.items() if not k.startswith("_")},
            content_data=content_data,
        ))
    
    total_pages = (total + page_size - 1) // page_size
    
    return BookmarkListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/bookmarks/check")
async def check_bookmark(
    content_type: ContentType,
    content_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Check if a specific content is bookmarked."""
    result = await db.execute(
        select(Bookmark).where(
            Bookmark.user_id == current_user.id,
            Bookmark.content_type == content_type.value,
            Bookmark.content_id == content_id,
        )
    )
    bookmark = result.scalar_one_or_none()
    return {"is_bookmarked": bookmark is not None, "bookmark_id": bookmark.id if bookmark else None}


@router.patch("/bookmarks/{bookmark_id}", response_model=BookmarkResponse)
async def update_bookmark(
    bookmark_id: int,
    bookmark_update: BookmarkUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a bookmark's notes."""
    result = await db.execute(
        select(Bookmark).where(
            Bookmark.id == bookmark_id,
            Bookmark.user_id == current_user.id,
        )
    )
    bookmark = result.scalar_one_or_none()
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    
    if bookmark_update.notes is not None:
        bookmark.notes = bookmark_update.notes
    
    await db.commit()
    await db.refresh(bookmark)
    
    content_data = await get_content_data(db, bookmark.content_type, bookmark.content_id)
    return BookmarkResponse(
        **{k: v for k, v in bookmark.__dict__.items() if not k.startswith("_")},
        content_data=content_data,
    )


@router.delete("/bookmarks/{bookmark_id}", status_code=204)
async def delete_bookmark(
    bookmark_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a bookmark."""
    result = await db.execute(
        select(Bookmark).where(
            Bookmark.id == bookmark_id,
            Bookmark.user_id == current_user.id,
        )
    )
    bookmark = result.scalar_one_or_none()
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    
    await db.delete(bookmark)
    await db.commit()


@router.delete("/bookmarks/by-content")
async def delete_bookmark_by_content(
    content_type: ContentType,
    content_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a bookmark by content type and ID."""
    result = await db.execute(
        select(Bookmark).where(
            Bookmark.user_id == current_user.id,
            Bookmark.content_type == content_type.value,
            Bookmark.content_id == content_id,
        )
    )
    bookmark = result.scalar_one_or_none()
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    
    await db.delete(bookmark)
    await db.commit()
    return {"message": "Bookmark deleted"}


# ============ Collection Endpoints ============

@router.post("/collections", response_model=CollectionResponse, status_code=201)
async def create_collection(
    collection: CollectionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new collection."""
    db_collection = Collection(
        user_id=current_user.id,
        name=collection.name,
        description=collection.description,
        is_public=collection.is_public,
        color=collection.color,
        icon=collection.icon,
    )
    db.add(db_collection)
    await db.commit()
    await db.refresh(db_collection)
    
    return CollectionResponse(
        **{k: v for k, v in db_collection.__dict__.items() if not k.startswith("_")},
        item_count=0,
    )


@router.get("/collections", response_model=CollectionListResponse)
async def list_collections(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List user's collections."""
    query = select(Collection).where(Collection.user_id == current_user.id)
    
    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Paginate
    query = query.order_by(Collection.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    collections = result.scalars().all()
    
    # Get item counts
    items = []
    for collection in collections:
        count_result = await db.execute(
            select(func.count()).where(CollectionItem.collection_id == collection.id)
        )
        item_count = count_result.scalar() or 0
        items.append(CollectionResponse(
            **{k: v for k, v in collection.__dict__.items() if not k.startswith("_")},
            item_count=item_count,
        ))
    
    total_pages = (total + page_size - 1) // page_size
    
    return CollectionListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/collections/{collection_id}", response_model=CollectionDetailResponse)
async def get_collection(
    collection_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a collection with its items."""
    result = await db.execute(
        select(Collection)
        .options(selectinload(Collection.items).selectinload(CollectionItem.bookmark))
        .where(
            Collection.id == collection_id,
            (Collection.user_id == current_user.id) | (Collection.is_public == True),
        )
    )
    collection = result.scalar_one_or_none()
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    # Build response with content data
    items_with_content = []
    for item in collection.items:
        content_data = await get_content_data(db, item.bookmark.content_type, item.bookmark.content_id)
        bookmark_response = BookmarkResponse(
            **{k: v for k, v in item.bookmark.__dict__.items() if not k.startswith("_")},
            content_data=content_data,
        )
        items_with_content.append({
            "id": item.id,
            "bookmark_id": item.bookmark_id,
            "order": item.order,
            "bookmark": bookmark_response,
        })
    
    return CollectionDetailResponse(
        **{k: v for k, v in collection.__dict__.items() if not k.startswith("_") and k != "items"},
        item_count=len(collection.items),
        items=items_with_content,
    )


@router.patch("/collections/{collection_id}", response_model=CollectionResponse)
async def update_collection(
    collection_id: int,
    collection_update: CollectionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a collection."""
    result = await db.execute(
        select(Collection).where(
            Collection.id == collection_id,
            Collection.user_id == current_user.id,
        )
    )
    collection = result.scalar_one_or_none()
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    update_data = collection_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(collection, key, value)
    
    await db.commit()
    await db.refresh(collection)
    
    # Get item count
    count_result = await db.execute(
        select(func.count()).where(CollectionItem.collection_id == collection.id)
    )
    item_count = count_result.scalar() or 0
    
    return CollectionResponse(
        **{k: v for k, v in collection.__dict__.items() if not k.startswith("_")},
        item_count=item_count,
    )


@router.delete("/collections/{collection_id}", status_code=204)
async def delete_collection(
    collection_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a collection."""
    result = await db.execute(
        select(Collection).where(
            Collection.id == collection_id,
            Collection.user_id == current_user.id,
        )
    )
    collection = result.scalar_one_or_none()
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    await db.delete(collection)
    await db.commit()


@router.post("/collections/{collection_id}/items", status_code=201)
async def add_to_collection(
    collection_id: int,
    request: AddToCollectionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a bookmark to a collection."""
    # Verify collection belongs to user
    collection_result = await db.execute(
        select(Collection).where(
            Collection.id == collection_id,
            Collection.user_id == current_user.id,
        )
    )
    if not collection_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Collection not found")
    
    # Verify bookmark belongs to user
    bookmark_result = await db.execute(
        select(Bookmark).where(
            Bookmark.id == request.bookmark_id,
            Bookmark.user_id == current_user.id,
        )
    )
    if not bookmark_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Bookmark not found")
    
    # Check if already in collection
    existing = await db.execute(
        select(CollectionItem).where(
            CollectionItem.collection_id == collection_id,
            CollectionItem.bookmark_id == request.bookmark_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Bookmark already in collection")
    
    # Get max order
    max_order_result = await db.execute(
        select(func.max(CollectionItem.order)).where(
            CollectionItem.collection_id == collection_id
        )
    )
    max_order = max_order_result.scalar() or 0
    
    item = CollectionItem(
        collection_id=collection_id,
        bookmark_id=request.bookmark_id,
        order=max_order + 1,
    )
    db.add(item)
    await db.commit()
    
    return {"message": "Added to collection", "item_id": item.id}


@router.delete("/collections/{collection_id}/items/{item_id}", status_code=204)
async def remove_from_collection(
    collection_id: int,
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove an item from a collection."""
    # Verify collection belongs to user
    collection_result = await db.execute(
        select(Collection).where(
            Collection.id == collection_id,
            Collection.user_id == current_user.id,
        )
    )
    if not collection_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Collection not found")
    
    # Delete item
    result = await db.execute(
        select(CollectionItem).where(
            CollectionItem.id == item_id,
            CollectionItem.collection_id == collection_id,
        )
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    await db.delete(item)
    await db.commit()


@router.post("/collections/{collection_id}/reorder")
async def reorder_collection_items(
    collection_id: int,
    request: ReorderCollectionItemsRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Reorder items in a collection."""
    # Verify collection belongs to user
    collection_result = await db.execute(
        select(Collection).where(
            Collection.id == collection_id,
            Collection.user_id == current_user.id,
        )
    )
    if not collection_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Collection not found")
    
    # Update order for each item
    for index, item_id in enumerate(request.item_ids):
        await db.execute(
            CollectionItem.__table__.update()
            .where(
                CollectionItem.id == item_id,
                CollectionItem.collection_id == collection_id,
            )
            .values(order=index)
        )
    
    await db.commit()
    return {"message": "Items reordered"}

