"""Seed pre-defined learning paths."""
import asyncio
import re
from datetime import datetime
from sqlalchemy import select
from app.db.database import AsyncSessionLocal
from app.models.learning_path import LearningPath
from app.models.learning import LearningResource


def generate_slug(title: str) -> str:
    """Generate a URL-friendly slug from title."""
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s_-]+', '-', slug)
    slug = slug.strip('-')
    return slug


# Pre-defined learning paths (resource titles will be mapped to IDs)
LEARNING_PATHS = [
    {
        "title": "AI Fundamentals for Absolute Beginners",
        "description": "Start your AI journey from zero. This path introduces AI concepts without technical jargon, perfect for those new to the field.",
        "level": "novice",
        "duration_hours": 8,
        "topics": ["artificial intelligence", "fundamentals", "introduction"],
        "resource_titles": [
            "Machine Learning Explained in 100 Seconds",
            "What is ChatGPT and How You Can Use It",
            "How AI could empower any business",
            "AI For Everyone",
        ],
        "is_featured": True,
    },
    {
        "title": "Understanding AI: A Visual Journey",
        "description": "Learn AI through visuals and intuitive explanations. Perfect for visual learners who want to understand how neural networks and machine learning actually work.",
        "level": "beginner",
        "duration_hours": 12,
        "topics": ["neural networks", "machine learning", "visual learning"],
        "resource_titles": [
            "But what is a neural network?",
            "Machine Learning Explained in 100 Seconds",
            "Google AI Essentials",
            "Elements of AI",
        ],
        "is_featured": True,
    },
    {
        "title": "AI for Business Leaders",
        "description": "Understand AI from a business perspective. Learn how to identify AI opportunities, communicate with technical teams, and lead AI initiatives.",
        "level": "beginner",
        "duration_hours": 15,
        "topics": ["business", "strategy", "leadership"],
        "resource_titles": [
            "How AI could empower any business",
            "AI For Everyone",
            "What is ChatGPT and How You Can Use It",
            "Google AI Essentials",
        ],
        "is_featured": True,
    },
    {
        "title": "Getting Started with AI Tools",
        "description": "Hands-on introduction to practical AI tools you can use today. From ChatGPT to other AI applications, learn to leverage AI in your daily work.",
        "level": "novice",
        "duration_hours": 6,
        "topics": ["practical ai", "tools", "chatgpt", "productivity"],
        "resource_titles": [
            "What is ChatGPT and How You Can Use It",
            "Machine Learning Explained in 100 Seconds",
            "Google AI Essentials",
        ],
        "is_featured": False,
    },
    {
        "title": "Complete AI Literacy Course",
        "description": "A comprehensive journey through AI fundamentals. Cover everything from basic concepts to understanding how AI impacts society and ethics.",
        "level": "beginner",
        "duration_hours": 40,
        "topics": ["artificial intelligence", "comprehensive", "ethics", "society"],
        "resource_titles": [
            "Machine Learning Explained in 100 Seconds",
            "But what is a neural network?",
            "AI For Everyone",
            "Elements of AI",
            "Google AI Essentials",
            "AI Foundations for Everyone",
        ],
        "is_featured": True,
    },
]


async def seed_learning_paths():
    """Seed learning paths with references to learning resources."""
    async with AsyncSessionLocal() as session:
        # First, get all learning resources to map titles to IDs
        resources_query = select(LearningResource).where(LearningResource.is_active == True)
        result = await session.execute(resources_query)
        resources = result.scalars().all()

        # Create title to ID mapping
        title_to_id = {r.title: r.id for r in resources}
        print(f"Found {len(title_to_id)} learning resources")

        added = 0
        skipped = 0

        for path_data in LEARNING_PATHS:
            slug = generate_slug(path_data["title"])

            # Check if path already exists
            existing_query = select(LearningPath).where(LearningPath.slug == slug)
            existing_result = await session.execute(existing_query)
            existing = existing_result.scalar_one_or_none()

            if existing:
                print(f"Skipped (exists): {path_data['title']}")
                skipped += 1
                continue

            # Map resource titles to IDs
            resource_ids = []
            for title in path_data.get("resource_titles", []):
                if title in title_to_id:
                    resource_ids.append(title_to_id[title])
                else:
                    print(f"  Warning: Resource not found: {title}")

            if not resource_ids:
                print(f"Skipped (no resources): {path_data['title']}")
                skipped += 1
                continue

            # Create learning path
            path = LearningPath(
                title=path_data["title"],
                slug=slug,
                description=path_data.get("description"),
                level=path_data["level"],
                duration_hours=path_data.get("duration_hours"),
                topics=path_data.get("topics", []),
                resource_ids=resource_ids,
                is_featured=path_data.get("is_featured", False),
                is_active=True,
            )

            session.add(path)
            added += 1
            print(f"Added: {path_data['title']} ({len(resource_ids)} resources)")

        await session.commit()
        print(f"\nSummary: Added {added} learning paths, skipped {skipped}")


if __name__ == "__main__":
    asyncio.run(seed_learning_paths())
