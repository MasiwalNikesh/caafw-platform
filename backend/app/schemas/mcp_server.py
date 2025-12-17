"""MCP Server schemas."""
from datetime import datetime
from typing import Optional, List
from .common import BaseResponse, PaginatedResponse


class MCPServerResponse(BaseResponse):
    """MCP Server response schema."""

    id: int
    name: str
    slug: str
    description: Optional[str] = None
    short_description: Optional[str] = None
    source: str
    category: str
    tags: Optional[List[str]] = None
    repository_url: Optional[str] = None
    documentation_url: Optional[str] = None
    npm_url: Optional[str] = None
    package_name: Optional[str] = None
    version: Optional[str] = None
    author: Optional[str] = None
    install_command: Optional[str] = None
    config_example: Optional[str] = None
    capabilities: Optional[List[str]] = None
    tools: Optional[List[str]] = None
    resources: Optional[List[str]] = None
    stars: int = 0
    downloads: int = 0
    forks: int = 0
    is_official: bool = False
    is_verified: bool = False
    is_featured: bool = False
    published_at: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class MCPServerListResponse(PaginatedResponse[MCPServerResponse]):
    """Paginated MCP server list response."""

    pass
