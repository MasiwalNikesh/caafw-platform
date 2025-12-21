"""Seed beginner-friendly learning resources."""
import asyncio
from datetime import datetime
from sqlalchemy import select
from app.db.database import AsyncSessionLocal
from app.models.learning import LearningResource, ResourceType

# Curated beginner-friendly resources
BEGINNER_RESOURCES = [
    {
        "source": "coursera",
        "resource_type": ResourceType.COURSE,
        "title": "AI For Everyone",
        "description": "AI is not only for engineers. If you want your organization to become better at using AI, this is the course to tell everyone to take. Andrew Ng explains AI in non-technical terms.",
        "provider": "Coursera",
        "instructor": "Andrew Ng",
        "institution": "DeepLearning.AI",
        "url": "https://www.coursera.org/learn/ai-for-everyone",
        "image_url": "https://d3njjcbhbojbot.cloudfront.net/api/utilities/v1/imageproxy/https://coursera-course-photos.s3.amazonaws.com/cb/3c4030d65011e8b7f5c785e31c4e0e/AI4E-Icon.jpg",
        "duration_minutes": 360,
        "level": "beginner",
        "is_free": False,
        "price": 0,  # Free to audit
        "rating": 4.8,
        "enrollments": 1000000,
        "topics": ["artificial intelligence", "machine learning", "business strategy"],
        "is_beginner_friendly": True,
        "source_difficulty": "beginner",
        "prerequisites": None,
    },
    {
        "source": "youtube",
        "resource_type": ResourceType.VIDEO,
        "title": "But what is a neural network?",
        "description": "An introduction to neural networks by 3Blue1Brown. Visual and intuitive explanation of how neural networks learn, perfect for visual learners.",
        "provider": "YouTube",
        "instructor": "3Blue1Brown",
        "url": "https://www.youtube.com/watch?v=aircAruvnKk",
        "image_url": "https://i.ytimg.com/vi/aircAruvnKk/maxresdefault.jpg",
        "duration_minutes": 19,
        "level": "beginner",
        "is_free": True,
        "rating": 4.9,
        "enrollments": 15000000,
        "topics": ["neural networks", "deep learning", "machine learning"],
        "is_beginner_friendly": True,
        "source_difficulty": "beginner",
        "prerequisites": None,
    },
    {
        "source": "google",
        "resource_type": ResourceType.COURSE,
        "title": "Google AI Essentials",
        "description": "Learn the fundamentals of AI from Google. No technical background required. Understand how AI works and how to use it responsibly.",
        "provider": "Google",
        "institution": "Google",
        "url": "https://grow.google/ai-essentials/",
        "duration_minutes": 600,
        "level": "beginner",
        "is_free": True,
        "rating": 4.7,
        "topics": ["artificial intelligence", "google ai", "productivity"],
        "is_beginner_friendly": True,
        "source_difficulty": "beginner",
        "prerequisites": None,
    },
    {
        "source": "ted",
        "resource_type": ResourceType.VIDEO,
        "title": "How AI could empower any business",
        "description": "Andrew Ng shares a vision for democratizing access to AI, exploring underappreciated opportunities for using AI to improve our lives.",
        "provider": "TED",
        "instructor": "Andrew Ng",
        "url": "https://www.ted.com/talks/andrew_ng_how_ai_could_empower_any_business",
        "image_url": "https://pi.tedcdn.com/r/talkstar-photos.s3.amazonaws.com/uploads/d9c4fd92-42c2-4e91-a7f8-4e60b3e0a6c2/AndrewNg_2022-embed.jpg",
        "duration_minutes": 14,
        "level": "beginner",
        "is_free": True,
        "rating": 4.8,
        "topics": ["artificial intelligence", "business", "accessibility"],
        "is_beginner_friendly": True,
        "source_difficulty": "beginner",
        "prerequisites": None,
    },
    {
        "source": "khan_academy",
        "resource_type": ResourceType.COURSE,
        "title": "Intro to Artificial Intelligence",
        "description": "Learn the basics of what AI is and how it works. Khan Academy's beginner-friendly introduction to artificial intelligence concepts.",
        "provider": "Khan Academy",
        "institution": "Khan Academy",
        "url": "https://www.khanacademy.org/computing/ai-for-education",
        "duration_minutes": 120,
        "level": "beginner",
        "is_free": True,
        "rating": 4.6,
        "topics": ["artificial intelligence", "education", "fundamentals"],
        "is_beginner_friendly": True,
        "source_difficulty": "beginner",
        "prerequisites": None,
    },
    {
        "source": "microsoft",
        "resource_type": ResourceType.COURSE,
        "title": "AI Skills Challenge",
        "description": "Free training from Microsoft to help you develop foundational AI skills. Learn about AI, machine learning, and Azure AI services.",
        "provider": "Microsoft Learn",
        "institution": "Microsoft",
        "url": "https://learn.microsoft.com/en-us/training/paths/get-started-with-artificial-intelligence/",
        "duration_minutes": 240,
        "level": "beginner",
        "is_free": True,
        "rating": 4.5,
        "topics": ["artificial intelligence", "azure", "machine learning"],
        "is_beginner_friendly": True,
        "source_difficulty": "beginner",
        "prerequisites": None,
    },
    {
        "source": "youtube",
        "resource_type": ResourceType.VIDEO,
        "title": "Machine Learning Explained in 100 Seconds",
        "description": "A quick, digestible introduction to machine learning by Fireship. Perfect for those who want a rapid overview before diving deeper.",
        "provider": "YouTube",
        "instructor": "Fireship",
        "url": "https://www.youtube.com/watch?v=PeMlggyqz0Y",
        "image_url": "https://i.ytimg.com/vi/PeMlggyqz0Y/maxresdefault.jpg",
        "duration_minutes": 2,
        "level": "beginner",
        "is_free": True,
        "rating": 4.9,
        "topics": ["machine learning", "quick overview", "fundamentals"],
        "is_beginner_friendly": True,
        "source_difficulty": "beginner",
        "prerequisites": None,
    },
    {
        "source": "ibm",
        "resource_type": ResourceType.COURSE,
        "title": "AI Foundations for Everyone",
        "description": "IBM's beginner course covering AI basics, including machine learning, deep learning, and neural networks. No programming required.",
        "provider": "IBM",
        "institution": "IBM",
        "url": "https://www.ibm.com/training/course/ai-foundations",
        "duration_minutes": 480,
        "level": "beginner",
        "is_free": True,
        "rating": 4.6,
        "topics": ["artificial intelligence", "machine learning", "deep learning"],
        "is_beginner_friendly": True,
        "source_difficulty": "beginner",
        "prerequisites": None,
    },
    {
        "source": "youtube",
        "resource_type": ResourceType.VIDEO,
        "title": "What is ChatGPT and How You Can Use It",
        "description": "A clear explanation of ChatGPT, how it works, and practical ways to use it in your daily life and work.",
        "provider": "YouTube",
        "instructor": "Kevin Stratvert",
        "url": "https://www.youtube.com/watch?v=e5XQUQ6xUWY",
        "image_url": "https://i.ytimg.com/vi/e5XQUQ6xUWY/maxresdefault.jpg",
        "duration_minutes": 25,
        "level": "beginner",
        "is_free": True,
        "rating": 4.8,
        "topics": ["chatgpt", "generative ai", "practical ai"],
        "is_beginner_friendly": True,
        "source_difficulty": "beginner",
        "prerequisites": None,
    },
    {
        "source": "elements_of_ai",
        "resource_type": ResourceType.COURSE,
        "title": "Elements of AI",
        "description": "A free online course created by the University of Helsinki and MinnaLearn. Learn what AI is, how it's made, and how it affects our lives.",
        "provider": "University of Helsinki",
        "institution": "University of Helsinki",
        "url": "https://www.elementsofai.com/",
        "duration_minutes": 1800,  # ~30 hours
        "level": "beginner",
        "is_free": True,
        "rating": 4.7,
        "enrollments": 800000,
        "topics": ["artificial intelligence", "ethics", "society"],
        "is_beginner_friendly": True,
        "source_difficulty": "beginner",
        "prerequisites": None,
    },
]


def generate_slug(title: str) -> str:
    """Generate a URL-friendly slug from title."""
    import re
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s_-]+', '-', slug)
    slug = slug.strip('-')
    return slug


async def seed_beginner_content():
    """Seed beginner-friendly learning resources."""
    async with AsyncSessionLocal() as session:
        added = 0
        skipped = 0

        for resource_data in BEGINNER_RESOURCES:
            # Check if resource already exists by title
            query = select(LearningResource).where(
                LearningResource.title == resource_data["title"]
            )
            result = await session.execute(query)
            existing = result.scalar_one_or_none()

            if existing:
                # Update existing resource to mark as beginner-friendly
                existing.is_beginner_friendly = True
                existing.source_difficulty = resource_data.get("source_difficulty", "beginner")
                skipped += 1
                print(f"Updated existing: {resource_data['title']}")
            else:
                # Create new resource
                resource = LearningResource(
                    source=resource_data["source"],
                    resource_type=resource_data["resource_type"],
                    title=resource_data["title"],
                    slug=generate_slug(resource_data["title"]),
                    description=resource_data.get("description"),
                    provider=resource_data.get("provider"),
                    instructor=resource_data.get("instructor"),
                    institution=resource_data.get("institution"),
                    url=resource_data["url"],
                    image_url=resource_data.get("image_url"),
                    duration_minutes=resource_data.get("duration_minutes"),
                    level=resource_data.get("level", "beginner"),
                    is_free=resource_data.get("is_free", True),
                    price=resource_data.get("price"),
                    rating=resource_data.get("rating"),
                    enrollments=resource_data.get("enrollments", 0),
                    topics=resource_data.get("topics", []),
                    is_beginner_friendly=True,
                    source_difficulty=resource_data.get("source_difficulty", "beginner"),
                    prerequisites=resource_data.get("prerequisites"),
                    is_featured=True,
                    is_active=True,
                    published_at=datetime.utcnow(),
                )
                session.add(resource)
                added += 1
                print(f"Added: {resource_data['title']}")

        await session.commit()
        print(f"\nSummary: Added {added} new resources, updated {skipped} existing resources")


if __name__ == "__main__":
    asyncio.run(seed_beginner_content())
