"""Celery tasks for data collection."""
import asyncio
import logging
from typing import List, Dict, Any
from celery import shared_task
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from app.db.database import AsyncSessionLocal
from app.collectors import (
    ProductHuntCollector,
    RSSNewsCollector,
    HackerNewsCollector,
    ArxivCollector,
    GitHubCollector,
    AdzunaCollector,
    TheMuseCollector,
    YouTubeCollector,
    MCPCollector,
)
from app.models.product import Product
from app.models.news import NewsArticle
from app.models.community import HackerNewsItem, GitHubRepo
from app.models.research import ResearchPaper
from app.models.job import Job
from app.models.learning import LearningResource
from app.models.mcp_server import MCPServer

logger = logging.getLogger(__name__)


def run_async(coro):
    """Run an async coroutine in a new event loop."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


async def upsert_items(model, items: List[Dict[str, Any]], unique_field: str = "external_id"):
    """Upsert items into the database."""
    if not items:
        return 0

    async with AsyncSessionLocal() as session:
        inserted = 0
        for item in items:
            try:
                # Check if exists
                query = select(model).where(getattr(model, unique_field) == item.get(unique_field))
                result = await session.execute(query)
                existing = result.scalar_one_or_none()

                if existing:
                    # Update existing
                    for key, value in item.items():
                        if hasattr(existing, key) and key != "id":
                            setattr(existing, key, value)
                else:
                    # Insert new
                    new_item = model(**item)
                    session.add(new_item)
                    inserted += 1

            except Exception as e:
                logger.error(f"Error upserting item: {e}")
                continue

        await session.commit()
        return inserted


@shared_task(name="app.tasks.collector_tasks.collect_products")
def collect_products():
    """Collect products from Product Hunt."""
    async def _collect():
        collector = ProductHuntCollector()
        try:
            data = await collector.run()
            inserted = await upsert_items(Product, data, "external_id")
            logger.info(f"Collected {len(data)} products, inserted {inserted} new")
            return {"collected": len(data), "inserted": inserted}
        except Exception as e:
            logger.error(f"Error collecting products: {e}")
            return {"error": str(e)}

    return run_async(_collect())


@shared_task(name="app.tasks.collector_tasks.collect_news")
def collect_news():
    """Collect news from RSS feeds."""
    async def _collect():
        collector = RSSNewsCollector()
        try:
            data = await collector.run()
            inserted = await upsert_items(NewsArticle, data, "external_id")
            logger.info(f"Collected {len(data)} news articles, inserted {inserted} new")
            return {"collected": len(data), "inserted": inserted}
        except Exception as e:
            logger.error(f"Error collecting news: {e}")
            return {"error": str(e)}

    return run_async(_collect())


@shared_task(name="app.tasks.collector_tasks.collect_hackernews")
def collect_hackernews():
    """Collect stories from Hacker News."""
    async def _collect():
        collector = HackerNewsCollector()
        try:
            data = await collector.run()
            inserted = await upsert_items(HackerNewsItem, data, "hn_id")
            logger.info(f"Collected {len(data)} HN items, inserted {inserted} new")
            return {"collected": len(data), "inserted": inserted}
        except Exception as e:
            logger.error(f"Error collecting HN: {e}")
            return {"error": str(e)}

    return run_async(_collect())


@shared_task(name="app.tasks.collector_tasks.collect_research")
def collect_research():
    """Collect research papers from arXiv."""
    async def _collect():
        collector = ArxivCollector()
        try:
            data = await collector.run()
            inserted = await upsert_items(ResearchPaper, data, "external_id")
            logger.info(f"Collected {len(data)} papers, inserted {inserted} new")
            return {"collected": len(data), "inserted": inserted}
        except Exception as e:
            logger.error(f"Error collecting research: {e}")
            return {"error": str(e)}

    return run_async(_collect())


@shared_task(name="app.tasks.collector_tasks.collect_github")
def collect_github():
    """Collect trending repositories from GitHub."""
    async def _collect():
        collector = GitHubCollector()
        try:
            data = await collector.run()
            # Use full_name as unique field for GitHub repos
            inserted = await upsert_items(GitHubRepo, data, "full_name")
            logger.info(f"Collected {len(data)} repos, inserted {inserted} new")
            return {"collected": len(data), "inserted": inserted}
        except Exception as e:
            logger.error(f"Error collecting GitHub: {e}")
            return {"error": str(e)}

    return run_async(_collect())


@shared_task(name="app.tasks.collector_tasks.collect_jobs")
def collect_jobs():
    """Collect jobs from Adzuna and The Muse."""
    async def _collect():
        total_collected = 0
        total_inserted = 0

        # Collect from Adzuna
        adzuna = AdzunaCollector()
        try:
            data = await adzuna.run()
            inserted = await upsert_items(Job, data, "external_id")
            total_collected += len(data)
            total_inserted += inserted
        except Exception as e:
            logger.error(f"Error collecting from Adzuna: {e}")

        # Collect from The Muse
        muse = TheMuseCollector()
        try:
            data = await muse.run()
            inserted = await upsert_items(Job, data, "external_id")
            total_collected += len(data)
            total_inserted += inserted
        except Exception as e:
            logger.error(f"Error collecting from The Muse: {e}")

        logger.info(f"Collected {total_collected} jobs, inserted {total_inserted} new")
        return {"collected": total_collected, "inserted": total_inserted}

    return run_async(_collect())


@shared_task(name="app.tasks.collector_tasks.collect_youtube")
def collect_youtube():
    """Collect AI educational videos from YouTube."""
    async def _collect():
        collector = YouTubeCollector()
        try:
            data = await collector.run()
            inserted = await upsert_items(LearningResource, data, "external_id")
            logger.info(f"Collected {len(data)} videos, inserted {inserted} new")
            return {"collected": len(data), "inserted": inserted}
        except Exception as e:
            logger.error(f"Error collecting YouTube: {e}")
            return {"error": str(e)}

    return run_async(_collect())


@shared_task(name="app.tasks.collector_tasks.collect_mcp")
def collect_mcp():
    """Collect MCP servers from awesome-mcp-servers."""
    async def _collect():
        collector = MCPCollector()
        try:
            data = await collector.run()
            inserted = await upsert_items(MCPServer, data, "slug")
            logger.info(f"Collected {len(data)} MCP servers, inserted {inserted} new")
            return {"collected": len(data), "inserted": inserted}
        except Exception as e:
            logger.error(f"Error collecting MCP: {e}")
            return {"error": str(e)}

    return run_async(_collect())


@shared_task(name="app.tasks.collector_tasks.collect_all")
def collect_all():
    """Run all collectors."""
    results = {}

    results["products"] = collect_products()
    results["news"] = collect_news()
    results["hackernews"] = collect_hackernews()
    results["research"] = collect_research()
    results["github"] = collect_github()
    results["jobs"] = collect_jobs()
    results["youtube"] = collect_youtube()
    results["mcp"] = collect_mcp()

    return results
