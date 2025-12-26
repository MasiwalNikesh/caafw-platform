"""Script to update content from various API sources."""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import AsyncSessionLocal
from app.collectors.product_hunt import ProductHuntCollector
from app.collectors.arxiv import ArxivCollector
from app.collectors.ai_jobs import AIJobsCollector
from app.collectors.ai_events import AIEventsCollector
from app.models.product import Product
from app.models.research import ResearchPaper
from app.models.job import Job
from app.models.event import Event


async def update_products(db: AsyncSession):
    """Update products from Product Hunt."""
    print("Updating products from Product Hunt...")
    collector = ProductHuntCollector()
    try:
        products = await collector.collect(first=50)
        print(f"  Fetched {len(products)} products")

        added = 0
        updated = 0
        for product_data in products:
            product_id = str(product_data.get('id'))
            # Check if product already exists by external_id
            existing = await db.scalar(
                select(Product).where(Product.external_id == product_id)
            )

            # Extract tags from topics
            topics = product_data.get('topics', {})
            if isinstance(topics, dict):
                edges = topics.get('edges', [])
                tags = [t['node']['name'] for t in edges if 'node' in t]
            else:
                tags = []

            # Create slug from name
            name = product_data.get('name', '')
            slug = name.lower().replace(' ', '-').replace('.', '')[:100] if name else product_id

            thumbnail = product_data.get('thumbnail')
            thumbnail_url = thumbnail.get('url') if isinstance(thumbnail, dict) else None

            if not existing:
                product = Product(
                    external_id=product_id,
                    source='product_hunt',
                    name=name,
                    slug=slug,
                    tagline=product_data.get('tagline'),
                    description=product_data.get('description'),
                    website_url=product_data.get('url'),
                    thumbnail_url=thumbnail_url,
                    upvotes=product_data.get('votesCount', 0),
                    comments_count=product_data.get('commentsCount', 0),
                    is_featured=product_data.get('featuredAt') is not None,
                    is_active=True,
                    tags=tags,
                )
                db.add(product)
                added += 1
            else:
                # Update existing product with latest data
                existing.upvotes = product_data.get('votesCount', existing.upvotes)
                existing.comments_count = product_data.get('commentsCount', existing.comments_count)
                updated += 1

        await db.commit()
        print(f"  Added {added} new products, updated {updated} existing")
    except Exception as e:
        print(f"  Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await collector.close()


async def update_research(db: AsyncSession):
    """Update research papers from arXiv."""
    print("Updating research papers from arXiv...")
    collector = ArxivCollector()
    try:
        papers = await collector.collect(max_results=50)
        print(f"  Fetched {len(papers)} papers")

        added = 0
        for paper_data in papers:
            arxiv_id = paper_data.get('arxiv_id') or paper_data.get('id', '').split('/')[-1]
            existing = await db.scalar(
                select(ResearchPaper).where(ResearchPaper.arxiv_id == arxiv_id)
            )
            if not existing:
                paper = ResearchPaper(
                    arxiv_id=arxiv_id,
                    title=paper_data.get('title'),
                    slug=paper_data.get('slug') or arxiv_id.replace('.', '-'),
                    abstract=paper_data.get('abstract') or paper_data.get('summary'),
                    authors=paper_data.get('authors', []),
                    categories=paper_data.get('categories', []),
                    pdf_url=paper_data.get('pdf_url'),
                    arxiv_url=paper_data.get('arxiv_url') or paper_data.get('link'),
                    is_active=True,
                )
                db.add(paper)
                added += 1

        await db.commit()
        print(f"  Added {added} new papers")
    except Exception as e:
        print(f"  Error: {e}")
    finally:
        await collector.close()


async def update_jobs(db: AsyncSession):
    """Update jobs from various sources."""
    print("Updating jobs...")
    collector = AIJobsCollector()
    try:
        # Collect raw data and transform it
        raw_jobs = await collector.collect()
        jobs_data = await collector.transform(raw_jobs)
        print(f"  Fetched {len(jobs_data)} jobs")

        added = 0
        for job_data in jobs_data:
            external_id = job_data.get('external_id')
            if external_id:
                existing = await db.scalar(
                    select(Job).where(Job.external_id == str(external_id))
                )
                if not existing:
                    job = Job(
                        external_id=str(external_id),
                        source=job_data.get('source', 'curated'),
                        title=job_data.get('title'),
                        slug=job_data.get('slug') or str(external_id),
                        description=job_data.get('description'),
                        company_name=job_data.get('company_name'),
                        company_logo=job_data.get('company_logo'),
                        company_url=job_data.get('company_url'),
                        location=job_data.get('location'),
                        city=job_data.get('city'),
                        state=job_data.get('state'),
                        country=job_data.get('country'),
                        is_remote=job_data.get('is_remote', False),
                        job_type=job_data.get('job_type'),
                        experience_level=job_data.get('experience_level'),
                        salary_min=job_data.get('salary_min'),
                        salary_max=job_data.get('salary_max'),
                        salary_currency=job_data.get('salary_currency'),
                        skills=job_data.get('skills'),
                        requirements=job_data.get('requirements'),
                        benefits=job_data.get('benefits'),
                        apply_url=job_data.get('apply_url'),
                        source_url=job_data.get('source_url'),
                        posted_at=job_data.get('posted_at'),
                        is_active=True,
                        is_featured=job_data.get('is_featured', False),
                    )
                    db.add(job)
                    added += 1

        await db.commit()
        print(f"  Added {added} new jobs")
    except Exception as e:
        print(f"  Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await collector.close()


async def update_events(db: AsyncSession):
    """Update events."""
    print("Updating events...")
    collector = AIEventsCollector()
    try:
        events_data = await collector.collect()
        print(f"  Fetched {len(events_data)} events")

        added = 0
        for event_data in events_data:
            title = event_data.get('title')
            if title:
                existing = await db.scalar(
                    select(Event).where(Event.title == title)
                )
                if not existing:
                    event = Event(
                        title=title,
                        slug=event_data.get('slug') or title.lower().replace(' ', '-')[:100],
                        description=event_data.get('description'),
                        event_type=event_data.get('event_type', 'conference'),
                        start_date=event_data.get('start_date'),
                        end_date=event_data.get('end_date'),
                        location=event_data.get('location'),
                        city=event_data.get('city'),
                        is_online=event_data.get('is_online', False),
                        url=event_data.get('url'),
                        is_active=True,
                    )
                    db.add(event)
                    added += 1

        await db.commit()
        print(f"  Added {added} new events")
    except Exception as e:
        print(f"  Error: {e}")
    finally:
        await collector.close()


async def main():
    """Run all content updates."""
    print("=" * 50)
    print("Starting content update...")
    print("=" * 50)

    async with AsyncSessionLocal() as db:
        await update_products(db)
        await update_research(db)
        await update_jobs(db)
        await update_events(db)

    print("=" * 50)
    print("Content update complete!")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
