"""AI Social Feed collector using Reddit's public API."""
from typing import Any, Dict, List, Optional
from datetime import datetime
import httpx
from .base import BaseCollector


class AISocialCollector(BaseCollector):
    """Collector for AI-related content from Reddit (no auth required)."""

    # AI-related subreddits
    AI_SUBREDDITS = [
        "MachineLearning",
        "artificial",
        "LocalLLaMA",
        "ChatGPT",
        "OpenAI",
        "StableDiffusion",
        "deeplearning",
        "learnmachinelearning",
        "MLQuestions",
        "LanguageTechnology",
    ]

    def __init__(self):
        super().__init__("ai_social")

    async def collect(
        self,
        subreddits: Optional[List[str]] = None,
        limit: int = 25,
        sort: str = "hot",  # hot, new, top, rising
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Collect posts from AI-related subreddits.

        Args:
            subreddits: List of subreddits to fetch from (defaults to AI_SUBREDDITS)
            limit: Number of posts per subreddit (max 100)
            sort: Sort method (hot, new, top, rising)
        """
        subreddits = subreddits or self.AI_SUBREDDITS[:5]
        limit = min(limit, 100)
        all_posts = []

        async with httpx.AsyncClient(
            timeout=30.0,
            headers={"User-Agent": "AI-Community-Platform/1.0"}
        ) as client:
            for subreddit in subreddits:
                try:
                    url = f"https://www.reddit.com/r/{subreddit}/{sort}.json"
                    response = await client.get(url, params={"limit": limit})

                    if response.status_code == 200:
                        data = response.json()
                        posts = data.get("data", {}).get("children", [])

                        for post in posts:
                            post_data = post.get("data", {})
                            post_data["_subreddit"] = subreddit
                            post_data["_sort"] = sort
                            all_posts.append(post_data)
                    else:
                        self.logger.warning(f"Failed to fetch r/{subreddit}: {response.status_code}")

                except Exception as e:
                    self.logger.error(f"Error fetching r/{subreddit}: {e}")
                    continue

        return all_posts

    async def transform(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform Reddit data to Tweet-compatible format for display."""
        posts = []
        for item in raw_data:
            # Skip stickied mod posts
            if item.get("stickied"):
                continue

            # Get thumbnail/preview image
            thumbnail = None
            if item.get("thumbnail") and item.get("thumbnail") not in ["self", "default", "nsfw", "spoiler"]:
                thumbnail = item.get("thumbnail")
            elif item.get("preview"):
                images = item.get("preview", {}).get("images", [])
                if images:
                    thumbnail = images[0].get("source", {}).get("url", "").replace("&amp;", "&")

            post = {
                "tweet_id": item.get("id"),
                "text": f"**{item.get('title', '')}**\n\n{item.get('selftext', '')[:500]}{'...' if len(item.get('selftext', '')) > 500 else ''}",
                "author_id": item.get("author_fullname", ""),
                "author_username": item.get("author", "unknown"),
                "author_name": f"r/{item.get('subreddit', '')}",
                "author_profile_image": None,  # Reddit doesn't expose this easily
                "author_verified": item.get("author_premium", False),
                "likes": item.get("ups", 0),
                "retweets": 0,  # Reddit doesn't have retweets
                "replies": item.get("num_comments", 0),
                "quotes": 0,
                "impressions": 0,
                "has_media": thumbnail is not None,
                "media_urls": [thumbnail] if thumbnail else None,
                "topic": item.get("_subreddit"),
                "search_query": item.get("link_flair_text"),
                "is_retweet": False,
                "is_reply": False,
                "tweeted_at": self._parse_timestamp(item.get("created_utc")),
                "extra_data": {
                    "url": f"https://reddit.com{item.get('permalink', '')}",
                    "subreddit": item.get("subreddit"),
                    "score": item.get("score", 0),
                    "upvote_ratio": item.get("upvote_ratio"),
                    "flair": item.get("link_flair_text"),
                    "is_video": item.get("is_video", False),
                    "domain": item.get("domain"),
                },
            }
            posts.append(post)

        # Sort by score (engagement)
        posts.sort(key=lambda x: x.get("likes", 0), reverse=True)
        return posts

    def _parse_timestamp(self, timestamp: Optional[float]) -> Optional[datetime]:
        """Parse Unix timestamp to datetime."""
        if not timestamp:
            return None
        try:
            return datetime.utcfromtimestamp(timestamp)
        except (ValueError, OSError):
            return None

    async def collect_trending(self, limit_per_sub: int = 10) -> List[Dict[str, Any]]:
        """Collect trending AI content from multiple subreddits."""
        return await self.collect(
            subreddits=self.AI_SUBREDDITS[:5],
            limit=limit_per_sub,
            sort="hot"
        )
