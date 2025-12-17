"""Twitter/X collector for AI-related tweets using OAuth 1.0a."""
from typing import Any, Dict, List, Optional
from datetime import datetime
import httpx
import hashlib
import hmac
import base64
import time
import secrets
from urllib.parse import quote, urlencode
from .base import BaseCollector
from app.core.config import settings


class TwitterCollector(BaseCollector):
    """Collector for Twitter/X API v2 using OAuth 1.0a."""

    BASE_URL = "https://api.twitter.com/2"

    # AI-related search topics for learning and courses
    AI_TOPICS = [
        "AI learning",
        "machine learning course",
        "deep learning tutorial",
        "LLM training",
        "ChatGPT tips",
        "AI education",
        "neural network",
        "NLP tutorial",
        "computer vision AI",
        "AI research",
        "generative AI",
        "AI tools",
        "MLOps",
        "AI agents",
        "prompt engineering",
    ]

    def __init__(self):
        super().__init__("twitter")
        self.api_key = settings.TWITTER_API_KEY
        self.api_secret = settings.TWITTER_API_SECRET
        self.access_token = settings.TWITTER_ACCESS_TOKEN
        self.access_token_secret = settings.TWITTER_ACCESS_TOKEN_SECRET

    def _generate_oauth_signature(
        self,
        method: str,
        url: str,
        params: Dict[str, str],
        oauth_params: Dict[str, str],
    ) -> str:
        """Generate OAuth 1.0a signature."""
        # Combine all parameters
        all_params = {**params, **oauth_params}

        # Sort and encode parameters
        sorted_params = sorted(all_params.items())
        param_string = "&".join(
            f"{quote(str(k), safe='')}={quote(str(v), safe='')}"
            for k, v in sorted_params
        )

        # Create signature base string
        signature_base = "&".join([
            method.upper(),
            quote(url, safe=""),
            quote(param_string, safe=""),
        ])

        # Create signing key
        signing_key = f"{quote(self.api_secret, safe='')}&{quote(self.access_token_secret, safe='')}"

        # Generate HMAC-SHA1 signature
        signature = hmac.new(
            signing_key.encode("utf-8"),
            signature_base.encode("utf-8"),
            hashlib.sha1,
        ).digest()

        return base64.b64encode(signature).decode("utf-8")

    def _get_oauth_header(self, method: str, url: str, params: Dict[str, str]) -> str:
        """Generate OAuth 1.0a Authorization header."""
        oauth_params = {
            "oauth_consumer_key": self.api_key,
            "oauth_token": self.access_token,
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_timestamp": str(int(time.time())),
            "oauth_nonce": secrets.token_hex(16),
            "oauth_version": "1.0",
        }

        # Generate signature
        signature = self._generate_oauth_signature(method, url, params, oauth_params)
        oauth_params["oauth_signature"] = signature

        # Build Authorization header
        auth_header = "OAuth " + ", ".join(
            f'{quote(k, safe="")}="{quote(v, safe="")}"'
            for k, v in sorted(oauth_params.items())
        )

        return auth_header

    async def collect(
        self,
        query: Optional[str] = None,
        topic: Optional[str] = None,
        max_results: int = 20,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Collect tweets from Twitter API v2 using OAuth 1.0a.

        Args:
            query: Custom search query (optional)
            topic: Predefined AI topic to search for
            max_results: Number of tweets to fetch (10-100)
        """
        if not all([self.api_key, self.api_secret, self.access_token, self.access_token_secret]):
            self.logger.warning("Twitter OAuth credentials not fully configured")
            return []

        # Build search query
        if query:
            search_query = query
        elif topic:
            search_query = f"{topic} -is:retweet lang:en"
        else:
            search_query = "(AI OR artificial intelligence OR machine learning) -is:retweet lang:en"

        # Clamp max_results to API limits
        max_results = max(10, min(100, max_results))

        url = f"{self.BASE_URL}/tweets/search/recent"
        params = {
            "query": search_query,
            "max_results": str(max_results),
            "tweet.fields": "id,text,author_id,created_at,public_metrics",
            "user.fields": "id,name,username,profile_image_url,verified",
            "expansions": "author_id",
        }

        try:
            # Generate OAuth header
            auth_header = self._get_oauth_header("GET", url, params)

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    url,
                    params=params,
                    headers={
                        "Authorization": auth_header,
                        "Content-Type": "application/json",
                    },
                )

                if response.status_code == 401:
                    self.logger.error(f"Twitter auth failed: {response.text}")
                    return []

                response.raise_for_status()
                data = response.json()

            if "errors" in data:
                self.logger.error(f"Twitter API errors: {data['errors']}")
                return []

            tweets = data.get("data", [])
            users = {u["id"]: u for u in data.get("includes", {}).get("users", [])}

            # Enrich tweets with user data
            enriched_tweets = []
            for tweet in tweets:
                author = users.get(tweet.get("author_id"), {})
                tweet["_author"] = author
                tweet["_topic"] = topic
                tweet["_search_query"] = search_query
                enriched_tweets.append(tweet)

            return enriched_tweets

        except httpx.HTTPStatusError as e:
            self.logger.error(f"HTTP error collecting from Twitter: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error collecting from Twitter: {e}")
            return []

    async def transform(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform Twitter API data to Tweet model format."""
        tweets = []
        for item in raw_data:
            author = item.get("_author", {})
            metrics = item.get("public_metrics", {})

            tweet = {
                "tweet_id": item.get("id"),
                "text": item.get("text"),
                "author_id": item.get("author_id"),
                "author_username": author.get("username", "unknown"),
                "author_name": author.get("name"),
                "author_profile_image": author.get("profile_image_url"),
                "author_verified": author.get("verified", False),
                "likes": metrics.get("like_count", 0),
                "retweets": metrics.get("retweet_count", 0),
                "replies": metrics.get("reply_count", 0),
                "quotes": metrics.get("quote_count", 0),
                "impressions": metrics.get("impression_count", 0),
                "has_media": False,
                "media_urls": None,
                "topic": item.get("_topic"),
                "search_query": item.get("_search_query"),
                "is_retweet": False,
                "is_reply": False,
                "tweeted_at": self._parse_date(item.get("created_at")),
            }
            tweets.append(tweet)

        return tweets

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse Twitter ISO date string."""
        if not date_str:
            return None
        try:
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            return dt.replace(tzinfo=None)
        except ValueError:
            return None

    async def collect_multiple_topics(
        self,
        topics: Optional[List[str]] = None,
        max_per_topic: int = 10,
    ) -> List[Dict[str, Any]]:
        """Collect tweets from multiple AI topics."""
        topics = topics or self.AI_TOPICS[:5]
        all_tweets = []

        for topic in topics:
            tweets = await self.collect(topic=topic, max_results=max_per_topic)
            all_tweets.extend(tweets)

        return all_tweets
