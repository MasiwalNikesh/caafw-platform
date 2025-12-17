"""Base collector class with common functionality."""
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class BaseCollector(ABC):
    """Base class for all data collectors."""

    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"collector.{name}")
        self._client: Optional[httpx.AsyncClient] = None

    async def get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=30.0,
                follow_redirects=True,
                headers={"User-Agent": "AI-Community-Platform/1.0"},
            )
        return self._client

    async def close(self):
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def fetch_url(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Optional[httpx.Response]:
        """Fetch URL with retry logic."""
        client = await self.get_client()
        try:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json_data,
            )
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as e:
            self.logger.error(f"HTTP error fetching {url}: {e}")
            raise
        except httpx.RequestError as e:
            self.logger.error(f"Request error fetching {url}: {e}")
            raise

    @abstractmethod
    async def collect(self, **kwargs) -> List[Dict[str, Any]]:
        """Collect data from the source. Must be implemented by subclasses."""
        pass

    @abstractmethod
    async def transform(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform raw data to model-compatible format. Must be implemented by subclasses."""
        pass

    async def run(self, **kwargs) -> List[Dict[str, Any]]:
        """Run the collector: collect and transform data."""
        self.logger.info(f"Starting collection from {self.name}")
        try:
            raw_data = await self.collect(**kwargs)
            self.logger.info(f"Collected {len(raw_data)} items from {self.name}")
            transformed = await self.transform(raw_data)
            self.logger.info(f"Transformed {len(transformed)} items from {self.name}")
            return transformed
        except Exception as e:
            self.logger.error(f"Error in {self.name} collector: {e}")
            raise
        finally:
            await self.close()
