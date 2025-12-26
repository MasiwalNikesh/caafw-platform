"""Admin API module."""
from fastapi import APIRouter

from . import dashboard, content, tags, categories, users, sources, audit, mcp, regions, regional_content

# Create main admin router
router = APIRouter()

# Include all admin sub-routers
router.include_router(dashboard.router, prefix="/dashboard", tags=["Admin - Dashboard"])
router.include_router(content.router, prefix="/content", tags=["Admin - Content Moderation"])
router.include_router(tags.router, prefix="/tags", tags=["Admin - Tags"])
router.include_router(categories.router, prefix="/categories", tags=["Admin - Categories"])
router.include_router(users.router, prefix="/users", tags=["Admin - Users"])
router.include_router(sources.router, prefix="/sources", tags=["Admin - API Sources"])
router.include_router(audit.router, prefix="/audit-log", tags=["Admin - Audit Log"])
router.include_router(mcp.router, prefix="/mcp", tags=["Admin - MCP Servers"])
router.include_router(regions.router, prefix="/regions", tags=["Admin - Regions"])
router.include_router(regional_content.router, prefix="/regional-content", tags=["Admin - Regional Content"])
