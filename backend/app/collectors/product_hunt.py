"""Product Hunt collector for AI products."""
from typing import Any, Dict, List, Optional
from datetime import datetime
import re
from .base import BaseCollector
from app.core.config import settings


# Topic to category mapping
TOPIC_TO_CATEGORY = {
    # AI/ML
    "artificial-intelligence": "ai-ml",
    "machine-learning": "ai-ml",
    "deep-learning": "ai-ml",
    "natural-language-processing": "ai-ml",
    "generative-ai": "ai-ml",
    "chatgpt": "ai-ml",
    "llm": "ai-ml",
    "ai-assistants": "ai-ml",
    "ai": "ai-ml",
    # Developer Tools
    "developer-tools": "developer-tools",
    "developer": "developer-tools",
    "no-code": "developer-tools",
    "low-code": "developer-tools",
    "apis": "developer-tools",
    "github": "developer-tools",
    "programming": "developer-tools",
    # Productivity
    "productivity": "productivity",
    "task-management": "productivity",
    "workflow": "productivity",
    "automation": "productivity",
    "calendar": "productivity",
    # Design
    "design": "design",
    "design-tools": "design",
    "figma": "design",
    "ui-ux": "design",
    "prototyping": "design",
    # Marketing
    "marketing": "marketing",
    "seo": "marketing",
    "social-media": "marketing",
    "content-marketing": "marketing",
    "email-marketing": "marketing",
    # Analytics
    "analytics": "analytics",
    "data": "analytics",
    "business-intelligence": "analytics",
    "metrics": "analytics",
    # Communication
    "communication": "communication",
    "messaging": "communication",
    "video-conferencing": "communication",
    "collaboration": "communication",
    # Education
    "education": "education",
    "learning": "education",
    "online-learning": "education",
    # Writing
    "writing": "writing",
    "writing-tools": "writing",
    "copywriting": "writing",
    "content-creation": "writing",
}


class ProductHuntCollector(BaseCollector):
    """Collector for Product Hunt API."""

    BASE_URL = "https://api.producthunt.com/v2/api/graphql"

    def __init__(self):
        super().__init__("product_hunt")
        self.token = settings.PRODUCT_HUNT_TOKEN

    def _get_headers(self) -> Dict[str, str]:
        """Get authentication headers."""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def collect(
        self,
        first: int = 50,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Collect products from Product Hunt."""
        if not self.token:
            self.logger.warning("No Product Hunt token configured")
            return []

        query = """
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
                        makers {
                            name
                            username
                        }
                    }
                }
            }
        }
        """

        variables = {"first": first}

        try:
            response = await self.fetch_url(
                self.BASE_URL,
                method="POST",
                headers=self._get_headers(),
                json_data={"query": query, "variables": variables},
            )
            data = response.json()
            edges = data.get("data", {}).get("posts", {}).get("edges", [])
            return [edge["node"] for edge in edges]
        except Exception as e:
            self.logger.error(f"Error collecting from Product Hunt: {e}")
            return []

    async def transform(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform Product Hunt data to product model format."""
        products = []
        for item in raw_data:
            slug = self._create_slug(item.get("name", ""))

            # Extract topics as tags
            topics = item.get("topics", {}).get("edges", [])
            tags = [t["node"]["name"] for t in topics]
            topic_slugs = [t["node"]["slug"] for t in topics]

            # Map topics to category slugs
            category_slugs = set()
            for topic_slug in topic_slugs:
                if topic_slug in TOPIC_TO_CATEGORY:
                    category_slugs.add(TOPIC_TO_CATEGORY[topic_slug])

            product = {
                "external_id": item.get("id"),
                "source": "product_hunt",
                "name": item.get("name"),
                "slug": slug,
                "tagline": item.get("tagline"),
                "description": item.get("description"),
                "website_url": item.get("website") or item.get("url"),
                "thumbnail_url": item.get("thumbnail", {}).get("url") if item.get("thumbnail") else None,
                "upvotes": item.get("votesCount", 0),
                "comments_count": item.get("commentsCount", 0),
                "tags": tags,
                "launched_at": self._parse_date(item.get("createdAt")),
                "is_featured": item.get("featuredAt") is not None,
                "extra_data": {
                    "makers": item.get("makers", []),
                    "product_hunt_url": item.get("url"),
                },
                # Category slugs for later assignment
                "_category_slugs": list(category_slugs),
            }
            products.append(product)

        return products

    def _create_slug(self, name: str) -> str:
        """Create URL-friendly slug from name."""
        slug = name.lower()
        slug = re.sub(r"[^a-z0-9\s-]", "", slug)
        slug = re.sub(r"[\s_]+", "-", slug)
        slug = re.sub(r"-+", "-", slug)
        return slug.strip("-")

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse ISO date string."""
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except ValueError:
            return None
