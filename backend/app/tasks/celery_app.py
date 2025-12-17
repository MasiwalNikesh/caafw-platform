"""Celery application configuration."""
from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

celery_app = Celery(
    "ai_community_platform",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.collector_tasks"],
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour
    worker_prefetch_multiplier=1,
    worker_concurrency=4,
)

# Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    # Collect news every 30 minutes
    "collect-news-every-30-minutes": {
        "task": "app.tasks.collector_tasks.collect_news",
        "schedule": crontab(minute="*/30"),
    },
    # Collect Hacker News every 15 minutes
    "collect-hackernews-every-15-minutes": {
        "task": "app.tasks.collector_tasks.collect_hackernews",
        "schedule": crontab(minute="*/15"),
    },
    # Collect research papers every 6 hours
    "collect-research-every-6-hours": {
        "task": "app.tasks.collector_tasks.collect_research",
        "schedule": crontab(hour="*/6", minute=0),
    },
    # Collect GitHub repos every hour
    "collect-github-every-hour": {
        "task": "app.tasks.collector_tasks.collect_github",
        "schedule": crontab(minute=0),
    },
    # Collect jobs every 2 hours
    "collect-jobs-every-2-hours": {
        "task": "app.tasks.collector_tasks.collect_jobs",
        "schedule": crontab(hour="*/2", minute=30),
    },
    # Collect products daily at midnight
    "collect-products-daily": {
        "task": "app.tasks.collector_tasks.collect_products",
        "schedule": crontab(hour=0, minute=0),
    },
    # Collect MCP servers daily at 1 AM
    "collect-mcp-daily": {
        "task": "app.tasks.collector_tasks.collect_mcp",
        "schedule": crontab(hour=1, minute=0),
    },
    # Collect YouTube videos daily at 2 AM
    "collect-youtube-daily": {
        "task": "app.tasks.collector_tasks.collect_youtube",
        "schedule": crontab(hour=2, minute=0),
    },
}
