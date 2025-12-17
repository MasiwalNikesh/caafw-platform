"""YouTube collector for AI educational content."""
from typing import Any, Dict, List, Optional
from datetime import datetime
import re
from .base import BaseCollector
from app.core.config import settings


class YouTubeCollector(BaseCollector):
    """Collector for YouTube Data API v3."""

    BASE_URL = "https://www.googleapis.com/youtube/v3"

    # Popular AI education channels
    AI_CHANNELS = [
        "UCWN3xxRkmTPmbKwht9FuE5A",  # Sentdex
        "UCbfYPyITQ-7l4upoX8nvctg",  # Two Minute Papers
        "UCYO_jab_esuFRV4b17AJtAw",  # 3Blue1Brown
        "UCcIXc5mJsHVYTZR1maL5l9w",  # StatQuest
        "UCr8O8l5cCX85Oem1d18EezQ",  # Computerphile
        "UCBcRF18a7Qf58cCRy5xuWwQ",  # Ben Eater
    ]

    def __init__(self):
        super().__init__("youtube")
        self.api_key = settings.YOUTUBE_API_KEY

    async def collect(
        self,
        search_query: str = "machine learning tutorial",
        max_results: int = 50,
        order: str = "relevance",
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Collect videos from YouTube."""
        if not self.api_key:
            self.logger.warning("YouTube API key not configured")
            return []

        params = {
            "key": self.api_key,
            "part": "snippet",
            "type": "video",
            "q": search_query,
            "maxResults": min(max_results, 50),
            "order": order,
            "relevanceLanguage": "en",
            "videoDuration": "medium",  # 4-20 minutes
        }

        try:
            response = await self.fetch_url(
                f"{self.BASE_URL}/search",
                params=params,
            )
            data = response.json()
            items = data.get("items", [])

            # Get video statistics for each video
            video_ids = [item["id"]["videoId"] for item in items]
            stats = await self._get_video_stats(video_ids)

            # Merge statistics with search results
            for item in items:
                video_id = item["id"]["videoId"]
                if video_id in stats:
                    item["statistics"] = stats[video_id]
                    item["contentDetails"] = stats.get(f"{video_id}_details", {})

            return items
        except Exception as e:
            self.logger.error(f"Error fetching from YouTube: {e}")
            return []

    async def _get_video_stats(self, video_ids: List[str]) -> Dict[str, Any]:
        """Get video statistics for multiple videos."""
        if not video_ids:
            return {}

        params = {
            "key": self.api_key,
            "part": "statistics,contentDetails",
            "id": ",".join(video_ids),
        }

        try:
            response = await self.fetch_url(
                f"{self.BASE_URL}/videos",
                params=params,
            )
            data = response.json()

            stats = {}
            for item in data.get("items", []):
                video_id = item["id"]
                stats[video_id] = item.get("statistics", {})
                stats[f"{video_id}_details"] = item.get("contentDetails", {})

            return stats
        except Exception as e:
            self.logger.error(f"Error fetching video stats: {e}")
            return {}

    async def transform(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform YouTube data to learning resource model format."""
        resources = []

        for item in raw_data:
            snippet = item.get("snippet", {})
            video_id = item.get("id", {}).get("videoId")
            statistics = item.get("statistics", {})
            content_details = item.get("contentDetails", {})

            if not video_id:
                continue

            # Parse duration
            duration_minutes = self._parse_duration(content_details.get("duration", ""))

            # Parse published date
            published_at = self._parse_date(snippet.get("publishedAt"))

            resource = {
                "external_id": video_id,
                "source": "youtube",
                "resource_type": "video",
                "title": snippet.get("title", ""),
                "slug": self._create_slug(snippet.get("title", ""), video_id),
                "description": snippet.get("description"),
                "provider": "YouTube",
                "instructor": snippet.get("channelTitle"),
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "image_url": snippet.get("thumbnails", {}).get("high", {}).get("url"),
                "thumbnail_url": snippet.get("thumbnails", {}).get("medium", {}).get("url"),
                "duration_minutes": duration_minutes,
                "is_free": True,
                "rating": None,
                "reviews_count": 0,
                "enrollments": int(statistics.get("viewCount", 0)),
                "topics": self._extract_topics(snippet.get("title", ""), snippet.get("description", "")),
                "published_at": published_at,
                "extra_data": {
                    "channel_id": snippet.get("channelId"),
                    "like_count": int(statistics.get("likeCount", 0)),
                    "comment_count": int(statistics.get("commentCount", 0)),
                    "tags": snippet.get("tags", []),
                },
            }
            resources.append(resource)

        return resources

    def _create_slug(self, title: str, video_id: str) -> str:
        """Create URL-friendly slug from title."""
        slug = title.lower()
        slug = re.sub(r"[^a-z0-9\s-]", "", slug)
        slug = re.sub(r"[\s_]+", "-", slug)
        slug = re.sub(r"-+", "-", slug)
        slug = slug.strip("-")[:500]
        return f"{slug}-{video_id}"

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse ISO date string."""
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except ValueError:
            return None

    def _parse_duration(self, duration: str) -> Optional[int]:
        """Parse ISO 8601 duration to minutes."""
        if not duration:
            return None

        # Format: PT#H#M#S
        match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration)
        if not match:
            return None

        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)

        return hours * 60 + minutes + (1 if seconds > 30 else 0)

    def _extract_topics(self, title: str, description: str) -> List[str]:
        """Extract AI-related topics from title and description."""
        text = f"{title} {description}".lower()

        topic_keywords = {
            "machine learning": ["machine learning", "ml"],
            "deep learning": ["deep learning", "neural network"],
            "nlp": ["nlp", "natural language", "text processing"],
            "computer vision": ["computer vision", "image recognition", "object detection"],
            "reinforcement learning": ["reinforcement learning", "rl"],
            "python": ["python"],
            "tensorflow": ["tensorflow"],
            "pytorch": ["pytorch"],
            "transformers": ["transformer", "attention mechanism"],
            "gpt": ["gpt", "language model"],
        }

        topics = []
        for topic, keywords in topic_keywords.items():
            if any(kw in text for kw in keywords):
                topics.append(topic)

        return topics[:10]  # Limit to 10 topics
