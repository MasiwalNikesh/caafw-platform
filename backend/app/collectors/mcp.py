"""MCP (Model Context Protocol) server collector."""
from typing import Any, Dict, List, Optional
from datetime import datetime
import re
from .base import BaseCollector
from app.core.config import settings


class MCPCollector(BaseCollector):
    """Collector for MCP server directories."""

    # GitHub API for awesome-mcp-servers repo
    GITHUB_API = "https://api.github.com"
    AWESOME_MCP_REPO = "punkpeye/awesome-mcp-servers"

    def __init__(self):
        super().__init__("mcp")
        self.token = settings.GITHUB_TOKEN

    def _get_headers(self) -> Dict[str, str]:
        """Get authentication headers."""
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    async def collect(self, **kwargs) -> List[Dict[str, Any]]:
        """Collect MCP servers from awesome-mcp-servers repo."""
        try:
            # Get README content from awesome-mcp-servers
            response = await self.fetch_url(
                f"{self.GITHUB_API}/repos/{self.AWESOME_MCP_REPO}/readme",
                headers=self._get_headers(),
            )
            data = response.json()

            # Decode base64 content
            import base64
            content = base64.b64decode(data.get("content", "")).decode("utf-8")

            # Parse the markdown to extract servers
            servers = self._parse_awesome_list(content)
            return servers
        except Exception as e:
            self.logger.error(f"Error fetching MCP servers: {e}")
            return []

    def _parse_awesome_list(self, content: str) -> List[Dict[str, Any]]:
        """Parse awesome-mcp-servers README markdown."""
        servers = []
        current_category = "other"

        lines = content.split("\n")

        for line in lines:
            line = line.strip()

            # Detect category headers
            if line.startswith("## "):
                current_category = self._normalize_category(line[3:].strip())
                continue

            # Detect list items with links
            if line.startswith("- [") or line.startswith("* ["):
                server = self._parse_list_item(line, current_category)
                if server:
                    servers.append(server)

        return servers

    def _parse_list_item(self, line: str, category: str) -> Optional[Dict[str, Any]]:
        """Parse a list item from the README."""
        # Pattern: - [Name](url) - Description
        pattern = r"[-*]\s*\[([^\]]+)\]\(([^)]+)\)\s*[-–]?\s*(.*)"
        match = re.match(pattern, line)

        if not match:
            return None

        name = match.group(1).strip()
        url = match.group(2).strip()
        description = match.group(3).strip()

        # Determine source based on URL
        source = "github"
        if "npmjs.com" in url:
            source = "npm"
        elif "mcp.so" in url:
            source = "mcp_registry"

        return {
            "name": name,
            "url": url,
            "description": description,
            "category": category,
            "source": source,
        }

    def _normalize_category(self, category: str) -> str:
        """Normalize category name."""
        category = category.lower().strip()

        category_map = {
            "database": "database",
            "databases": "database",
            "cloud": "cloud",
            "cloud services": "cloud",
            "aws": "cloud",
            "developer tools": "developer_tools",
            "development": "developer_tools",
            "communication": "communication",
            "messaging": "communication",
            "search": "search",
            "productivity": "productivity",
            "ai": "ai_ml",
            "machine learning": "ai_ml",
            "storage": "storage",
            "file": "storage",
            "monitoring": "monitoring",
            "observability": "monitoring",
        }

        for key, value in category_map.items():
            if key in category:
                return value

        return "other"

    async def transform(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform parsed data to MCP server model format."""
        servers = []

        for item in raw_data:
            name = item.get("name", "")
            url = item.get("url", "")

            # Create slug
            slug = self._create_slug(name)

            # Determine if it's a GitHub repo to potentially fetch more info
            is_github = "github.com" in url

            server = {
                "external_id": slug,
                "source": item.get("source", "github"),
                "name": name,
                "slug": slug,
                "description": item.get("description"),
                "short_description": item.get("description", "")[:500] if item.get("description") else None,
                "category": item.get("category", "other"),
                "repository_url": url if is_github else None,
                "npm_url": url if "npmjs.com" in url else None,
                "documentation_url": url if not is_github and "npmjs.com" not in url else None,
                "is_official": "modelcontextprotocol" in url.lower(),
                "tags": self._extract_tags(name, item.get("description", "")),
            }
            servers.append(server)

        return servers

    def _create_slug(self, name: str) -> str:
        """Create URL-friendly slug from name."""
        slug = name.lower()
        slug = re.sub(r"[^a-z0-9\s-]", "", slug)
        slug = re.sub(r"[\s_]+", "-", slug)
        slug = re.sub(r"-+", "-", slug)
        return slug.strip("-")[:300]

    def _extract_tags(self, name: str, description: str) -> List[str]:
        """Extract relevant tags from name and description."""
        text = f"{name} {description}".lower()

        tag_keywords = {
            "postgresql": ["postgres", "postgresql"],
            "mongodb": ["mongo", "mongodb"],
            "mysql": ["mysql"],
            "redis": ["redis"],
            "aws": ["aws", "amazon"],
            "gcp": ["gcp", "google cloud"],
            "azure": ["azure", "microsoft"],
            "slack": ["slack"],
            "discord": ["discord"],
            "github": ["github"],
            "gitlab": ["gitlab"],
            "docker": ["docker"],
            "kubernetes": ["kubernetes", "k8s"],
            "api": ["api", "rest"],
            "web": ["web", "http"],
            "file": ["file", "filesystem"],
            "search": ["search", "elasticsearch"],
        }

        tags = []
        for tag, keywords in tag_keywords.items():
            if any(kw in text for kw in keywords):
                tags.append(tag)

        return tags[:10]
