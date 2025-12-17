"""AI Events collector from multiple free sources."""
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import httpx
import re
from .base import BaseCollector


class AIEventsCollector(BaseCollector):
    """Collector for AI-related events from free public sources."""

    # Major AI conferences and events (curated list)
    MAJOR_AI_EVENTS = [
        {
            "title": "NeurIPS 2025 - Conference on Neural Information Processing Systems",
            "event_type": "conference",
            "description": "The premier annual machine learning conference, featuring cutting-edge research in neural networks, deep learning, and AI.",
            "organizer_name": "NeurIPS Foundation",
            "city": "San Diego",
            "country": "USA",
            "is_online": False,
            "url": "https://neurips.cc",
            "is_free": False,
            "topics": ["Machine Learning", "Neural Networks", "Deep Learning", "AI Research"],
            "starts_at": "2025-12-09",
            "ends_at": "2025-12-15",
        },
        {
            "title": "ICML 2025 - International Conference on Machine Learning",
            "event_type": "conference",
            "description": "The leading international academic conference in machine learning, featuring research presentations and workshops.",
            "organizer_name": "ICML",
            "city": "Vancouver",
            "country": "Canada",
            "is_online": False,
            "url": "https://icml.cc",
            "is_free": False,
            "topics": ["Machine Learning", "AI Research", "Deep Learning"],
            "starts_at": "2025-07-21",
            "ends_at": "2025-07-27",
        },
        {
            "title": "CVPR 2025 - Computer Vision and Pattern Recognition",
            "event_type": "conference",
            "description": "The premier annual computer vision event comprising the main conference and several co-located workshops and tutorials.",
            "organizer_name": "IEEE/CVF",
            "city": "Nashville",
            "country": "USA",
            "is_online": False,
            "url": "https://cvpr.thecvf.com",
            "is_free": False,
            "topics": ["Computer Vision", "Pattern Recognition", "Deep Learning", "Image Processing"],
            "starts_at": "2025-06-14",
            "ends_at": "2025-06-20",
        },
        {
            "title": "ACL 2025 - Association for Computational Linguistics",
            "event_type": "conference",
            "description": "The premier conference of the Association for Computational Linguistics, covering NLP and computational linguistics.",
            "organizer_name": "ACL",
            "city": "Vienna",
            "country": "Austria",
            "is_online": True,
            "url": "https://2025.aclweb.org",
            "is_free": False,
            "topics": ["NLP", "Computational Linguistics", "LLMs", "Language Models"],
            "starts_at": "2025-07-27",
            "ends_at": "2025-08-01",
        },
        {
            "title": "AI Summit San Francisco 2025",
            "event_type": "summit",
            "description": "The world's largest AI event for business, bringing together the AI ecosystem to discuss real-world applications.",
            "organizer_name": "AI Summit",
            "city": "San Francisco",
            "country": "USA",
            "is_online": False,
            "url": "https://theaisummit.com/sanfrancisco",
            "is_free": False,
            "topics": ["AI Business", "Enterprise AI", "AI Strategy", "AI Applications"],
            "starts_at": "2025-09-10",
            "ends_at": "2025-09-11",
        },
        {
            "title": "Google I/O 2025",
            "event_type": "conference",
            "description": "Google's annual developer conference featuring AI/ML announcements, Gemini updates, and Android innovations.",
            "organizer_name": "Google",
            "city": "Mountain View",
            "country": "USA",
            "is_online": True,
            "url": "https://io.google",
            "is_free": True,
            "topics": ["Google AI", "Gemini", "Android", "Cloud AI", "TensorFlow"],
            "starts_at": "2025-05-14",
            "ends_at": "2025-05-15",
        },
        {
            "title": "Microsoft Build 2025",
            "event_type": "conference",
            "description": "Microsoft's flagship developer conference with focus on AI, Copilot, Azure AI, and developer tools.",
            "organizer_name": "Microsoft",
            "city": "Seattle",
            "country": "USA",
            "is_online": True,
            "url": "https://build.microsoft.com",
            "is_free": True,
            "topics": ["Microsoft AI", "Azure AI", "Copilot", "OpenAI", "Developer Tools"],
            "starts_at": "2025-05-19",
            "ends_at": "2025-05-21",
        },
        {
            "title": "AWS re:Invent 2025",
            "event_type": "conference",
            "description": "Amazon Web Services' annual cloud computing conference featuring AI/ML services and innovations.",
            "organizer_name": "Amazon Web Services",
            "city": "Las Vegas",
            "country": "USA",
            "is_online": True,
            "url": "https://reinvent.awsevents.com",
            "is_free": False,
            "topics": ["AWS", "Cloud AI", "SageMaker", "Bedrock", "Generative AI"],
            "starts_at": "2025-12-01",
            "ends_at": "2025-12-05",
        },
    ]

    # Online AI meetups and webinars (recurring)
    RECURRING_EVENTS = [
        {
            "title": "MLOps Community Meetup",
            "event_type": "meetup",
            "description": "Weekly community meetup discussing MLOps best practices, tools, and real-world implementations.",
            "organizer_name": "MLOps Community",
            "is_online": True,
            "url": "https://mlops.community",
            "is_free": True,
            "topics": ["MLOps", "ML Engineering", "Model Deployment"],
        },
        {
            "title": "Weights & Biases AI Workshop",
            "event_type": "workshop",
            "description": "Hands-on workshop on experiment tracking, model management, and ML workflows.",
            "organizer_name": "Weights & Biases",
            "is_online": True,
            "url": "https://wandb.ai/events",
            "is_free": True,
            "topics": ["ML Experiments", "Model Training", "W&B"],
        },
        {
            "title": "Hugging Face Community Sprint",
            "event_type": "hackathon",
            "description": "Community hackathon focused on contributing to open-source AI projects and the Hugging Face ecosystem.",
            "organizer_name": "Hugging Face",
            "is_online": True,
            "url": "https://huggingface.co/events",
            "is_free": True,
            "topics": ["Open Source AI", "Transformers", "NLP", "LLMs"],
        },
        {
            "title": "LangChain AI Agents Webinar",
            "event_type": "webinar",
            "description": "Deep dive into building AI agents with LangChain, covering architecture, tools, and best practices.",
            "organizer_name": "LangChain",
            "is_online": True,
            "url": "https://langchain.com/events",
            "is_free": True,
            "topics": ["AI Agents", "LangChain", "LLM Applications", "RAG"],
        },
    ]

    def __init__(self):
        super().__init__("ai_events")

    async def collect(self, include_recurring: bool = True, **kwargs) -> List[Dict[str, Any]]:
        """Collect AI events from curated sources."""
        events = []

        # Add major conferences
        events.extend(self.MAJOR_AI_EVENTS)

        # Add recurring events with generated dates
        if include_recurring:
            for event in self.RECURRING_EVENTS:
                # Generate upcoming dates for recurring events
                for weeks_ahead in [1, 2, 3, 4]:
                    event_copy = event.copy()
                    event_date = datetime.now() + timedelta(weeks=weeks_ahead)
                    event_copy["starts_at"] = event_date.strftime("%Y-%m-%d")
                    event_copy["ends_at"] = event_date.strftime("%Y-%m-%d")
                    event_copy["title"] = f"{event['title']} - {event_date.strftime('%B %d, %Y')}"
                    events.append(event_copy)

        # Try to fetch from Luma (public events)
        luma_events = await self._fetch_luma_events()
        events.extend(luma_events)

        return events

    async def _fetch_luma_events(self) -> List[Dict[str, Any]]:
        """Fetch AI-related events from Luma's public API."""
        events = []

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                # Search for AI-related events on Luma
                for query in ["artificial intelligence", "machine learning", "AI workshop"]:
                    response = await client.get(
                        "https://api.lu.ma/public/v1/calendar/list-events",
                        params={"query": query, "limit": 10},
                        headers={"User-Agent": "AI-Community-Platform/1.0"}
                    )

                    if response.status_code == 200:
                        data = response.json()
                        for entry in data.get("entries", []):
                            event = entry.get("event", {})
                            if event:
                                events.append({
                                    "title": event.get("name", ""),
                                    "event_type": "meetup",
                                    "description": event.get("description", ""),
                                    "organizer_name": "Luma",
                                    "city": event.get("geo_address_info", {}).get("city"),
                                    "country": event.get("geo_address_info", {}).get("country"),
                                    "is_online": event.get("location_type") == "online",
                                    "url": f"https://lu.ma/{event.get('url', '')}",
                                    "is_free": True,
                                    "topics": ["AI", "Tech"],
                                    "starts_at": event.get("start_at", "")[:10] if event.get("start_at") else None,
                                    "ends_at": event.get("end_at", "")[:10] if event.get("end_at") else None,
                                    "image_url": event.get("cover_url"),
                                    "external_id": f"luma_{event.get('api_id', '')}",
                                })
        except Exception as e:
            self.logger.warning(f"Failed to fetch Luma events: {e}")

        return events

    async def transform(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform event data to Event model format."""
        events = []

        for item in raw_data:
            slug = self._create_slug(item.get("title", ""))

            event = {
                "external_id": item.get("external_id") or f"curated_{slug}",
                "source": "curated" if not item.get("external_id") else "luma",
                "event_type": item.get("event_type", "other"),
                "title": item.get("title", ""),
                "slug": slug,
                "description": item.get("description", ""),
                "short_description": (item.get("description", "") or "")[:200],
                "organizer_name": item.get("organizer_name"),
                "city": item.get("city"),
                "country": item.get("country"),
                "is_online": item.get("is_online", False),
                "url": item.get("url", ""),
                "image_url": item.get("image_url"),
                "is_free": item.get("is_free", False),
                "topics": item.get("topics", []),
                "tags": item.get("topics", []),
                "is_featured": item.get("event_type") == "conference",
                "is_active": True,
                "starts_at": self._parse_date(item.get("starts_at")),
                "ends_at": self._parse_date(item.get("ends_at")),
            }
            events.append(event)

        return events

    def _create_slug(self, title: str) -> str:
        """Create URL-friendly slug from title."""
        slug = title.lower()
        slug = re.sub(r"[^a-z0-9\s-]", "", slug)
        slug = re.sub(r"[\s_]+", "-", slug)
        slug = re.sub(r"-+", "-", slug)
        return slug.strip("-")[:100]

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string."""
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str[:10], "%Y-%m-%d")
        except (ValueError, TypeError):
            return None
