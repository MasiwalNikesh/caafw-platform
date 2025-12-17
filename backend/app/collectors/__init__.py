"""Data collectors for various sources."""
from .base import BaseCollector
from .product_hunt import ProductHuntCollector
from .rss_news import RSSNewsCollector
from .hackernews import HackerNewsCollector
from .arxiv import ArxivCollector
from .github import GitHubCollector
from .jobs import AdzunaCollector, TheMuseCollector
from .youtube import YouTubeCollector
from .mcp import MCPCollector

__all__ = [
    "BaseCollector",
    "ProductHuntCollector",
    "RSSNewsCollector",
    "HackerNewsCollector",
    "ArxivCollector",
    "GitHubCollector",
    "AdzunaCollector",
    "TheMuseCollector",
    "YouTubeCollector",
    "MCPCollector",
]
