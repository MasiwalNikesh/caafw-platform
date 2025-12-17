"""Job collectors for Adzuna and The Muse APIs."""
from typing import Any, Dict, List, Optional
from datetime import datetime
import re
from .base import BaseCollector
from app.core.config import settings


class AdzunaCollector(BaseCollector):
    """Collector for Adzuna Jobs API."""

    BASE_URL = "https://api.adzuna.com/v1/api/jobs"

    def __init__(self):
        super().__init__("adzuna")
        self.app_id = settings.ADZUNA_APP_ID
        self.api_key = settings.ADZUNA_API_KEY

    async def collect(
        self,
        country: str = "us",
        what: str = "artificial intelligence machine learning",
        results_per_page: int = 50,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Collect jobs from Adzuna."""
        if not self.app_id or not self.api_key:
            self.logger.warning("Adzuna credentials not configured")
            return []

        params = {
            "app_id": self.app_id,
            "app_key": self.api_key,
            "results_per_page": results_per_page,
            "what": what,
            "content-type": "application/json",
        }

        try:
            response = await self.fetch_url(
                f"{self.BASE_URL}/{country}/search/1",
                params=params,
            )
            data = response.json()
            return data.get("results", [])
        except Exception as e:
            self.logger.error(f"Error fetching from Adzuna: {e}")
            return []

    async def transform(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform Adzuna data to job model format."""
        jobs = []

        for item in raw_data:
            posted_at = self._parse_date(item.get("created"))

            # Extract location components
            location = item.get("location", {})
            location_parts = location.get("display_name", "").split(", ")

            job = {
                "external_id": item.get("id"),
                "source": "adzuna",
                "title": item.get("title", ""),
                "slug": self._create_slug(item.get("title", ""), item.get("id", "")),
                "description": item.get("description"),
                "company_name": item.get("company", {}).get("display_name", "Unknown"),
                "location": location.get("display_name"),
                "city": location_parts[0] if location_parts else None,
                "country": location_parts[-1] if len(location_parts) > 1 else None,
                "is_remote": "remote" in item.get("title", "").lower() or "remote" in item.get("description", "").lower(),
                "job_type": item.get("contract_type"),
                "salary_min": int(item.get("salary_min")) if item.get("salary_min") else None,
                "salary_max": int(item.get("salary_max")) if item.get("salary_max") else None,
                "salary_currency": "USD",
                "apply_url": item.get("redirect_url"),
                "source_url": item.get("redirect_url"),
                "posted_at": posted_at,
                "extra_data": {
                    "category": item.get("category", {}).get("label"),
                    "latitude": item.get("latitude"),
                    "longitude": item.get("longitude"),
                },
            }
            jobs.append(job)

        return jobs

    def _create_slug(self, title: str, job_id: str) -> str:
        """Create URL-friendly slug from title."""
        slug = title.lower()
        slug = re.sub(r"[^a-z0-9\s-]", "", slug)
        slug = re.sub(r"[\s_]+", "-", slug)
        slug = re.sub(r"-+", "-", slug)
        slug = slug.strip("-")[:250]
        return f"{slug}-{job_id}"

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string."""
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except ValueError:
            return None


class TheMuseCollector(BaseCollector):
    """Collector for The Muse Jobs API."""

    BASE_URL = "https://www.themuse.com/api/public/jobs"

    def __init__(self):
        super().__init__("the_muse")
        self.api_key = settings.THE_MUSE_API_KEY

    async def collect(
        self,
        category: str = "Data Science",
        level: Optional[str] = None,
        page: int = 1,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Collect jobs from The Muse."""
        params = {
            "category": category,
            "page": page,
        }

        if self.api_key:
            params["api_key"] = self.api_key

        if level:
            params["level"] = level

        try:
            response = await self.fetch_url(self.BASE_URL, params=params)
            data = response.json()
            return data.get("results", [])
        except Exception as e:
            self.logger.error(f"Error fetching from The Muse: {e}")
            return []

    async def transform(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform The Muse data to job model format."""
        jobs = []

        for item in raw_data:
            # Extract location
            locations = item.get("locations", [])
            location_name = locations[0].get("name") if locations else None

            # Parse location components
            city, state, country = None, None, None
            if location_name:
                parts = location_name.split(", ")
                city = parts[0] if parts else None
                if len(parts) > 1:
                    state = parts[1]
                if len(parts) > 2:
                    country = parts[2]

            # Check for remote
            is_remote = any("remote" in loc.get("name", "").lower() for loc in locations)

            # Get company info
            company = item.get("company", {})

            posted_at = self._parse_date(item.get("publication_date"))

            job = {
                "external_id": str(item.get("id")),
                "source": "the_muse",
                "title": item.get("name", ""),
                "slug": self._create_slug(item.get("name", ""), str(item.get("id", ""))),
                "description": item.get("contents"),
                "description_html": item.get("contents"),
                "company_name": company.get("name", "Unknown"),
                "company_url": f"https://www.themuse.com/companies/{company.get('short_name', '')}",
                "location": location_name,
                "city": city,
                "state": state,
                "country": country,
                "is_remote": is_remote,
                "experience_level": item.get("levels", [{}])[0].get("name") if item.get("levels") else None,
                "apply_url": item.get("refs", {}).get("landing_page"),
                "source_url": item.get("refs", {}).get("landing_page"),
                "posted_at": posted_at,
                "extra_data": {
                    "categories": [cat.get("name") for cat in item.get("categories", [])],
                    "tags": item.get("tags", []),
                    "company_id": company.get("id"),
                },
            }
            jobs.append(job)

        return jobs

    def _create_slug(self, title: str, job_id: str) -> str:
        """Create URL-friendly slug from title."""
        slug = title.lower()
        slug = re.sub(r"[^a-z0-9\s-]", "", slug)
        slug = re.sub(r"[\s_]+", "-", slug)
        slug = re.sub(r"-+", "-", slug)
        slug = slug.strip("-")[:250]
        return f"{slug}-{job_id}"

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string."""
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except ValueError:
            return None
