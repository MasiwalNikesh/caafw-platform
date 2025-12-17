"""Celery tasks module."""
from .celery_app import celery_app
from .collector_tasks import (
    collect_products,
    collect_news,
    collect_hackernews,
    collect_research,
    collect_github,
    collect_jobs,
    collect_youtube,
    collect_mcp,
    collect_all,
)

__all__ = [
    "celery_app",
    "collect_products",
    "collect_news",
    "collect_hackernews",
    "collect_research",
    "collect_github",
    "collect_jobs",
    "collect_youtube",
    "collect_mcp",
    "collect_all",
]
