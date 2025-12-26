"""Seed admin users, tags, categories, and API sources for testing."""
import asyncio
from datetime import datetime
from sqlalchemy import select
from app.db.database import AsyncSessionLocal
from app.models.user import User, UserProfile
from app.models.admin import UserRole, Tag, ContentCategory, APISource
from app.core.security import get_password_hash


# Admin users to create
ADMIN_USERS = [
    {
        "email": "superadmin@caafw.org",
        "password": "Admin123!",
        "name": "Super Admin",
        "role": UserRole.SUPER_ADMIN,
    },
    {
        "email": "admin@caafw.org",
        "password": "Admin123!",
        "name": "Admin User",
        "role": UserRole.ADMIN,
    },
    {
        "email": "moderator@caafw.org",
        "password": "Mod123!",
        "name": "Moderator",
        "role": UserRole.MODERATOR,
    },
]

# Initial tags to create
INITIAL_TAGS = [
    {"name": "LLM", "description": "Large Language Models", "is_featured": True},
    {"name": "GPT", "description": "GPT models and applications", "is_featured": True},
    {"name": "Machine Learning", "description": "ML algorithms and techniques", "is_featured": True},
    {"name": "Deep Learning", "description": "Neural networks and deep learning", "is_featured": True},
    {"name": "NLP", "description": "Natural Language Processing", "is_featured": True},
    {"name": "Computer Vision", "description": "Image and video AI", "is_featured": True},
    {"name": "RAG", "description": "Retrieval Augmented Generation", "is_featured": False},
    {"name": "Fine-tuning", "description": "Model fine-tuning techniques", "is_featured": False},
    {"name": "OpenAI", "description": "OpenAI products and research", "is_featured": True},
    {"name": "Anthropic", "description": "Anthropic products and research", "is_featured": True},
    {"name": "Google AI", "description": "Google AI products", "is_featured": False},
    {"name": "Open Source", "description": "Open source AI tools and models", "is_featured": True},
    {"name": "PyTorch", "description": "PyTorch framework", "is_featured": False},
    {"name": "Transformers", "description": "Transformer architecture", "is_featured": False},
    {"name": "AI Safety", "description": "AI alignment and safety", "is_featured": False},
]

# Initial categories to create
INITIAL_CATEGORIES = [
    {
        "name": "AI Research",
        "description": "Academic research and papers",
        "icon": "📚",
        "children": [
            {"name": "NLP Research", "description": "Natural language processing research"},
            {"name": "Computer Vision Research", "description": "CV papers and breakthroughs"},
            {"name": "Reinforcement Learning", "description": "RL research"},
        ],
    },
    {
        "name": "AI Tools",
        "description": "AI products and developer tools",
        "icon": "🛠️",
        "children": [
            {"name": "LLM Applications", "description": "Apps built on LLMs"},
            {"name": "Developer Tools", "description": "Tools for AI developers"},
            {"name": "Productivity Tools", "description": "AI-powered productivity"},
        ],
    },
    {
        "name": "AI News",
        "description": "Latest AI industry news",
        "icon": "📰",
        "children": [
            {"name": "Product Launches", "description": "New AI product announcements"},
            {"name": "Company News", "description": "AI company updates"},
            {"name": "Policy & Regulation", "description": "AI policy news"},
        ],
    },
    {
        "name": "Learning",
        "description": "Educational resources",
        "icon": "🎓",
        "children": [
            {"name": "Tutorials", "description": "Step-by-step tutorials"},
            {"name": "Courses", "description": "Online courses"},
            {"name": "Documentation", "description": "API docs and guides"},
        ],
    },
    {
        "name": "Career",
        "description": "Jobs and career resources",
        "icon": "💼",
        "children": [
            {"name": "Job Listings", "description": "AI job opportunities"},
            {"name": "Career Advice", "description": "Career guidance"},
        ],
    },
]

# API sources to seed (fetch_frequency is in minutes)
API_SOURCES = [
    {
        "name": "arXiv AI",
        "slug": "arxiv-ai",
        "source_type": "api",
        "url": "https://export.arxiv.org/api/query?search_query=cat:cs.AI&sortBy=submittedDate&sortOrder=descending",
        "is_active": True,
        "auto_approve": True,
        "fetch_frequency": 60,  # 1 hour
    },
    {
        "name": "Hacker News",
        "slug": "hackernews",
        "source_type": "api",
        "url": "https://hacker-news.firebaseio.com/v0/topstories.json",
        "is_active": True,
        "auto_approve": True,
        "fetch_frequency": 30,  # 30 minutes
    },
    {
        "name": "OpenAI Blog",
        "slug": "openai-blog",
        "source_type": "rss",
        "url": "https://openai.com/blog/rss.xml",
        "is_active": True,
        "auto_approve": True,
        "fetch_frequency": 120,  # 2 hours
    },
    {
        "name": "Anthropic News",
        "slug": "anthropic-news",
        "source_type": "rss",
        "url": "https://www.anthropic.com/news/rss.xml",
        "is_active": True,
        "auto_approve": True,
        "fetch_frequency": 120,  # 2 hours
    },
    {
        "name": "DeepMind Blog",
        "slug": "deepmind-blog",
        "source_type": "rss",
        "url": "https://www.deepmind.com/blog/rss.xml",
        "is_active": True,
        "auto_approve": True,
        "fetch_frequency": 120,  # 2 hours
    },
    {
        "name": "The Batch (DeepLearning.AI)",
        "slug": "the-batch",
        "source_type": "rss",
        "url": "https://www.deeplearning.ai/the-batch/feed/",
        "is_active": True,
        "auto_approve": False,
        "fetch_frequency": 1440,  # 24 hours (1 day)
    },
    {
        "name": "Papers With Code",
        "slug": "papers-with-code",
        "source_type": "api",
        "url": "https://paperswithcode.com/api/v1/papers/",
        "is_active": True,
        "auto_approve": True,
        "fetch_frequency": 60,  # 1 hour
    },
]


def create_slug(name: str) -> str:
    """Create URL-friendly slug from name."""
    import re
    slug = name.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")[:100]


async def seed_admin_users(db):
    """Create admin users."""
    print("\n=== Seeding Admin Users ===")
    created = 0

    for user_data in ADMIN_USERS:
        # Check if user exists
        result = await db.execute(
            select(User).where(User.email == user_data["email"])
        )
        existing = result.scalar_one_or_none()

        if existing:
            print(f"  User already exists: {user_data['email']}")
            # Update role if needed
            if existing.role != user_data["role"]:
                existing.role = user_data["role"]
                print(f"    Updated role to: {user_data['role'].value}")
            continue

        # Create new user
        user = User(
            email=user_data["email"],
            password_hash=get_password_hash(user_data["password"]),
            name=user_data["name"],
            role=user_data["role"],
            is_active=True,
            is_verified=True,
        )
        db.add(user)
        await db.flush()

        # Create profile
        profile = UserProfile(
            user_id=user.id,
            has_completed_quiz=True,
            ai_level="expert",
        )
        db.add(profile)

        print(f"  Created: {user_data['email']} ({user_data['role'].value})")
        created += 1

    await db.commit()
    print(f"  Total created: {created}")
    return created


async def seed_tags(db):
    """Create initial tags."""
    print("\n=== Seeding Tags ===")
    created = 0

    for tag_data in INITIAL_TAGS:
        slug = create_slug(tag_data["name"])

        # Check if tag exists
        result = await db.execute(
            select(Tag).where(Tag.slug == slug)
        )
        existing = result.scalar_one_or_none()

        if existing:
            print(f"  Tag already exists: {tag_data['name']}")
            continue

        tag = Tag(
            name=tag_data["name"],
            slug=slug,
            description=tag_data.get("description"),
            is_featured=tag_data.get("is_featured", False),
        )
        db.add(tag)
        print(f"  Created tag: {tag_data['name']}")
        created += 1

    await db.commit()
    print(f"  Total created: {created}")
    return created


async def seed_categories(db):
    """Create initial categories."""
    print("\n=== Seeding Categories ===")
    created = 0

    for sort_order, cat_data in enumerate(INITIAL_CATEGORIES):
        slug = create_slug(cat_data["name"])

        # Check if category exists
        result = await db.execute(
            select(ContentCategory).where(ContentCategory.slug == slug)
        )
        existing = result.scalar_one_or_none()

        if existing:
            print(f"  Category already exists: {cat_data['name']}")
            parent_id = existing.id
        else:
            # Create parent category
            category = ContentCategory(
                name=cat_data["name"],
                slug=slug,
                description=cat_data.get("description"),
                icon=cat_data.get("icon"),
                sort_order=sort_order,
                is_active=True,
            )
            db.add(category)
            await db.flush()
            parent_id = category.id
            print(f"  Created category: {cat_data['name']}")
            created += 1

        # Create children
        for child_order, child_data in enumerate(cat_data.get("children", [])):
            child_slug = create_slug(child_data["name"])

            result = await db.execute(
                select(ContentCategory).where(ContentCategory.slug == child_slug)
            )
            child_existing = result.scalar_one_or_none()

            if child_existing:
                print(f"    Child already exists: {child_data['name']}")
                continue

            child = ContentCategory(
                name=child_data["name"],
                slug=child_slug,
                description=child_data.get("description"),
                parent_id=parent_id,
                sort_order=child_order,
                is_active=True,
            )
            db.add(child)
            print(f"    Created child: {child_data['name']}")
            created += 1

    await db.commit()
    print(f"  Total created: {created}")
    return created


async def seed_api_sources(db):
    """Create API sources."""
    print("\n=== Seeding API Sources ===")
    created = 0

    for source_data in API_SOURCES:
        # Check if source exists
        result = await db.execute(
            select(APISource).where(APISource.slug == source_data["slug"])
        )
        existing = result.scalar_one_or_none()

        if existing:
            print(f"  Source already exists: {source_data['name']}")
            continue

        source = APISource(
            name=source_data["name"],
            slug=source_data["slug"],
            source_type=source_data["source_type"],
            url=source_data["url"],
            is_active=source_data.get("is_active", True),
            auto_approve=source_data.get("auto_approve", False),
            fetch_frequency=source_data.get("fetch_frequency", 3600),
        )
        db.add(source)
        print(f"  Created source: {source_data['name']}")
        created += 1

    await db.commit()
    print(f"  Total created: {created}")
    return created


async def main():
    """Run all seed functions."""
    print("=" * 50)
    print("ADMIN SEED SCRIPT")
    print("=" * 50)

    async with AsyncSessionLocal() as db:
        try:
            users_created = await seed_admin_users(db)
            tags_created = await seed_tags(db)
            categories_created = await seed_categories(db)
            sources_created = await seed_api_sources(db)

            print("\n" + "=" * 50)
            print("SEED COMPLETE!")
            print("=" * 50)
            print(f"  Admin users created: {users_created}")
            print(f"  Tags created: {tags_created}")
            print(f"  Categories created: {categories_created}")
            print(f"  API sources created: {sources_created}")
            print("\n" + "=" * 50)
            print("LOGIN CREDENTIALS:")
            print("=" * 50)
            print("  Super Admin: superadmin@caafw.org / Admin123!")
            print("  Admin:       admin@caafw.org / Admin123!")
            print("  Moderator:   moderator@caafw.org / Mod123!")
            print("=" * 50)

        except Exception as e:
            print(f"\nError during seeding: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(main())
