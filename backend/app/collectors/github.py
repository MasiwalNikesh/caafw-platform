"""GitHub collector for trending repositories."""
from typing import Any, Dict, List, Optional
from datetime import datetime
import re
from .base import BaseCollector
from app.core.config import settings


class GitHubCollector(BaseCollector):
    """Collector for GitHub trending repositories."""

    BASE_URL = "https://api.github.com"
    TRENDING_URL = "https://api.gitterapp.com/repositories"

    # AI-related topics to search for
    AI_TOPICS = [
        "machine-learning",
        "deep-learning",
        "artificial-intelligence",
        "nlp",
        "computer-vision",
        "transformers",
        "llm",
        "gpt",
        "langchain",
        "neural-network",
    ]

    def __init__(self):
        super().__init__("github")
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

    async def collect(
        self,
        method: str = "search",
        language: Optional[str] = None,
        since: str = "daily",
        limit: int = 50,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Collect repositories from GitHub."""
        if method == "trending":
            return await self._get_trending(language, since)
        return await self._search_repos(language, limit)

    async def _get_trending(
        self,
        language: Optional[str],
        since: str
    ) -> List[Dict[str, Any]]:
        """Get trending repositories from unofficial API."""
        try:
            params = {"since": since}
            if language:
                params["language"] = language

            response = await self.fetch_url(self.TRENDING_URL, params=params)
            return response.json()
        except Exception as e:
            self.logger.error(f"Error fetching trending repos: {e}")
            return []

    async def _search_repos(
        self,
        language: Optional[str],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Search repositories using GitHub API."""
        all_repos = []
        seen_ids = set()

        # Search for each topic individually to avoid query complexity issues
        search_topics = ["machine-learning", "deep-learning", "llm", "artificial-intelligence", "langchain"]
        per_topic_limit = max(limit // len(search_topics), 10)

        for topic in search_topics:
            query = f"topic:{topic} stars:>100"
            if language:
                query += f" language:{language}"

            params = {
                "q": query,
                "sort": "stars",
                "order": "desc",
                "per_page": per_topic_limit,
            }

            try:
                response = await self.fetch_url(
                    f"{self.BASE_URL}/search/repositories",
                    headers=self._get_headers(),
                    params=params,
                )
                data = response.json()
                for repo in data.get("items", []):
                    if repo["id"] not in seen_ids:
                        seen_ids.add(repo["id"])
                        all_repos.append(repo)
            except Exception as e:
                self.logger.warning(f"Error searching topic {topic}: {e}")
                continue

        # Sort by stars and limit
        all_repos.sort(key=lambda x: x.get("stargazers_count", 0), reverse=True)
        return all_repos[:limit]

    async def transform(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform GitHub data to repository model format."""
        repos = []

        for item in raw_data:
            # Handle both trending API and search API formats
            if "author" in item:
                # Trending API format
                repo = self._transform_trending_item(item)
            else:
                # GitHub search API format
                repo = self._transform_search_item(item)

            if repo:
                repos.append(repo)

        return repos

    def _transform_trending_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Transform trending API item."""
        return {
            "github_id": 0,  # Not available in trending API
            "name": item.get("name", ""),
            "full_name": f"{item.get('author', '')}/{item.get('name', '')}",
            "description": item.get("description"),
            "owner": item.get("author", ""),
            "owner_type": "User",
            "owner_avatar": item.get("avatar"),
            "url": item.get("url", ""),
            "homepage": None,
            "language": item.get("language"),
            "topics": [],
            "stars": item.get("stars", 0),
            "forks": item.get("forks", 0),
            "watchers": 0,
            "open_issues": 0,
            "is_fork": False,
            "is_archived": False,
            "trending_rank": item.get("rank"),
            "stars_today": item.get("currentPeriodStars", 0),
            "extra_data": {
                "built_by": item.get("builtBy", []),
            },
        }

    def _transform_search_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Transform GitHub search API item."""
        owner = item.get("owner", {})

        # Parse dates
        created_at = self._parse_date(item.get("created_at"))
        updated_at = self._parse_date(item.get("updated_at"))
        pushed_at = self._parse_date(item.get("pushed_at"))

        return {
            "github_id": item.get("id"),
            "name": item.get("name", ""),
            "full_name": item.get("full_name", ""),
            "description": item.get("description"),
            "owner": owner.get("login", ""),
            "owner_type": owner.get("type", "User"),
            "owner_avatar": owner.get("avatar_url"),
            "url": item.get("html_url", ""),
            "homepage": item.get("homepage"),
            "language": item.get("language"),
            "topics": item.get("topics", []),
            "stars": item.get("stargazers_count", 0),
            "forks": item.get("forks_count", 0),
            "watchers": item.get("watchers_count", 0),
            "open_issues": item.get("open_issues_count", 0),
            "default_branch": item.get("default_branch", "main"),
            "is_fork": item.get("fork", False),
            "is_archived": item.get("archived", False),
            "license_name": item.get("license", {}).get("name") if item.get("license") else None,
            "repo_created_at": created_at,
            "repo_updated_at": updated_at,
            "pushed_at": pushed_at,
        }

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse ISO date string (returns naive datetime for DB compatibility)."""
        if not date_str:
            return None
        try:
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            # Convert to naive datetime for DB compatibility
            return dt.replace(tzinfo=None)
        except ValueError:
            return None
