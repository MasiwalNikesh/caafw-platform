"""Product Hunt collector for AI products."""
from typing import Any, Dict, List, Optional
from datetime import datetime
import re
from .base import BaseCollector
from app.core.config import settings


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
