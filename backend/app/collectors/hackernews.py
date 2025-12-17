"""Hacker News collector."""
from typing import Any, Dict, List, Optional
from datetime import datetime
import asyncio
from .base import BaseCollector


class HackerNewsCollector(BaseCollector):
    """Collector for Hacker News API."""

    BASE_URL = "https://hacker-news.firebaseio.com/v0"
    ALGOLIA_URL = "https://hn.algolia.com/api/v1"

    def __init__(self):
        super().__init__("hackernews")

    async def collect(
        self,
        story_type: str = "top",
        limit: int = 100,
        search_query: Optional[str] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Collect stories from Hacker News."""
        if search_query:
            return await self._search_stories(search_query, limit)
        return await self._get_stories(story_type, limit)

    async def _get_stories(self, story_type: str, limit: int) -> List[Dict[str, Any]]:
        """Get stories by type (top, new, best)."""
        endpoint_map = {
            "top": "topstories",
            "new": "newstories",
            "best": "beststories",
        }
        endpoint = endpoint_map.get(story_type, "topstories")

        try:
            # Get story IDs
            response = await self.fetch_url(f"{self.BASE_URL}/{endpoint}.json")
            story_ids = response.json()[:limit]

            # Fetch story details in batches
            stories = []
            batch_size = 20
            for i in range(0, len(story_ids), batch_size):
                batch_ids = story_ids[i:i + batch_size]
                batch_tasks = [self._get_item(sid) for sid in batch_ids]
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)

                for result in batch_results:
                    if isinstance(result, dict):
                        stories.append(result)

            return stories
        except Exception as e:
            self.logger.error(f"Error fetching HN stories: {e}")
            return []

    async def _get_item(self, item_id: int) -> Optional[Dict[str, Any]]:
        """Get a single HN item by ID."""
        try:
            response = await self.fetch_url(f"{self.BASE_URL}/item/{item_id}.json")
            return response.json()
        except Exception as e:
            self.logger.error(f"Error fetching HN item {item_id}: {e}")
            return None

    async def _search_stories(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Search stories using Algolia API."""
        try:
            params = {
                "query": query,
                "tags": "story",
                "hitsPerPage": limit,
            }
            response = await self.fetch_url(
                f"{self.ALGOLIA_URL}/search",
                params=params,
            )
            data = response.json()
            return data.get("hits", [])
        except Exception as e:
            self.logger.error(f"Error searching HN: {e}")
            return []

    async def transform(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform HN data to model format."""
        items = []

        for item in raw_data:
            # Handle both Firebase and Algolia response formats
            hn_id = item.get("id") or item.get("objectID")
            if not hn_id:
                continue

            # Convert Algolia format to Firebase format if needed
            if "objectID" in item:
                item = self._convert_algolia_item(item)

            posted_at = None
            if item.get("time"):
                posted_at = datetime.fromtimestamp(item["time"])

            transformed = {
                "hn_id": int(hn_id),
                "item_type": item.get("type", "story"),
                "title": item.get("title"),
                "url": item.get("url"),
                "text": item.get("text"),
                "author": item.get("by"),
                "score": item.get("score", 0),
                "comments_count": item.get("descendants", 0),
                "is_dead": item.get("dead", False),
                "is_deleted": item.get("deleted", False),
                "posted_at": posted_at,
                "extra_data": {
                    "kids": item.get("kids", []),
                },
            }
            items.append(transformed)

        return items

    def _convert_algolia_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Algolia search result to Firebase format."""
        return {
            "id": item.get("objectID"),
            "type": "story",
            "title": item.get("title"),
            "url": item.get("url"),
            "by": item.get("author"),
            "score": item.get("points", 0),
            "descendants": item.get("num_comments", 0),
            "time": item.get("created_at_i"),
        }
