"""MCP Server models."""
from datetime import datetime
from typing import Optional, List
from enum import Enum
from sqlalchemy import String, Text, Integer, Boolean, JSON, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base
from .base import TimestampMixin


class MCPCategory(str, Enum):
    """MCP Server category enum."""
    DATABASE = "database"
    CLOUD = "cloud"
    DEVELOPER_TOOLS = "developer_tools"
    COMMUNICATION = "communication"
    SEARCH = "search"
    PRODUCTIVITY = "productivity"
    AI_ML = "ai_ml"
    STORAGE = "storage"
    MONITORING = "monitoring"
    OTHER = "other"


class MCPServer(Base, TimestampMixin):
    """MCP Server model."""

    __tablename__ = "mcp_servers"

    id: Mapped[int] = mapped_column(primary_key=True)
    external_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True)
    source: Mapped[str] = mapped_column(String(50), nullable=False)  # mcp_registry, mcp_central, github

    # Basic Info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(300), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    short_description: Mapped[Optional[str]] = mapped_column(String(500))

    # Category
    category: Mapped[MCPCategory] = mapped_column(SQLEnum(MCPCategory), default=MCPCategory.OTHER)
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON)

    # URLs
    repository_url: Mapped[Optional[str]] = mapped_column(String(500))
    documentation_url: Mapped[Optional[str]] = mapped_column(String(500))
    npm_url: Mapped[Optional[str]] = mapped_column(String(500))

    # Package Info
    package_name: Mapped[Optional[str]] = mapped_column(String(255))
    version: Mapped[Optional[str]] = mapped_column(String(50))
    author: Mapped[Optional[str]] = mapped_column(String(255))

    # Installation
    install_command: Mapped[Optional[str]] = mapped_column(Text)
    config_example: Mapped[Optional[str]] = mapped_column(Text)

    # Capabilities
    capabilities: Mapped[Optional[List[str]]] = mapped_column(JSON)  # tools, resources, prompts
    tools: Mapped[Optional[List[str]]] = mapped_column(JSON)
    resources: Mapped[Optional[List[str]]] = mapped_column(JSON)

    # Metrics
    stars: Mapped[int] = mapped_column(Integer, default=0)
    downloads: Mapped[int] = mapped_column(Integer, default=0)
    forks: Mapped[int] = mapped_column(Integer, default=0)

    # Status
    is_official: Mapped[bool] = mapped_column(Boolean, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Dates
    published_at: Mapped[Optional[datetime]] = mapped_column()
    last_updated: Mapped[Optional[datetime]] = mapped_column()

    # Extra data
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON)

    def __repr__(self) -> str:
        return f"<MCPServer {self.name}>"
