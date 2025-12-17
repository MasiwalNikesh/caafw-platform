"""MCP Servers API endpoints."""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.database import get_db
from app.models.mcp_server import MCPServer, MCPCategory
from app.schemas.mcp_server import MCPServerResponse, MCPServerListResponse

router = APIRouter()


@router.get("", response_model=MCPServerListResponse)
async def list_mcp_servers(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    category: Optional[str] = None,
    is_official: Optional[bool] = None,
    is_verified: Optional[bool] = None,
    is_featured: Optional[bool] = None,
    search: Optional[str] = None,
    sort_by: str = Query(default="stars", pattern="^(created_at|stars|downloads|name)$"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db),
):
    """List MCP servers with filtering and pagination."""
    query = select(MCPServer).where(MCPServer.is_active == True)

    # Apply filters
    if category:
        query = query.where(MCPServer.category == category)
    if is_official is not None:
        query = query.where(MCPServer.is_official == is_official)
    if is_verified is not None:
        query = query.where(MCPServer.is_verified == is_verified)
    if is_featured is not None:
        query = query.where(MCPServer.is_featured == is_featured)
    if search:
        query = query.where(
            MCPServer.name.ilike(f"%{search}%") |
            MCPServer.description.ilike(f"%{search}%")
        )

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    # Apply sorting
    sort_column = getattr(MCPServer, sort_by)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc().nullslast())
    else:
        query = query.order_by(sort_column.asc().nullsfirst())

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    servers = result.scalars().all()

    total_pages = (total + page_size - 1) // page_size

    return MCPServerListResponse(
        items=[MCPServerResponse.model_validate(s) for s in servers],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )


@router.get("/categories", response_model=List[dict])
async def list_categories():
    """List available MCP server categories."""
    return [
        {"value": c.value, "label": c.name.replace("_", " ").title()}
        for c in MCPCategory
    ]


@router.get("/{server_id}", response_model=MCPServerResponse)
async def get_mcp_server(
    server_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a single MCP server by ID."""
    query = select(MCPServer).where(
        MCPServer.id == server_id,
        MCPServer.is_active == True
    )
    result = await db.execute(query)
    server = result.scalar_one_or_none()

    if not server:
        raise HTTPException(status_code=404, detail="MCP Server not found")

    return MCPServerResponse.model_validate(server)


@router.get("/slug/{slug}", response_model=MCPServerResponse)
async def get_mcp_server_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a single MCP server by slug."""
    query = select(MCPServer).where(
        MCPServer.slug == slug,
        MCPServer.is_active == True
    )
    result = await db.execute(query)
    server = result.scalar_one_or_none()

    if not server:
        raise HTTPException(status_code=404, detail="MCP Server not found")

    return MCPServerResponse.model_validate(server)
