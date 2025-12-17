"""AI Jobs collector with curated job listings from major AI companies."""
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import random
import re
from .base import BaseCollector


class AIJobsCollector(BaseCollector):
    """Collector for curated AI job listings."""

    # Major AI companies hiring
    AI_COMPANIES = [
        {"name": "OpenAI", "logo": "https://logo.clearbit.com/openai.com", "url": "https://openai.com/careers"},
        {"name": "Anthropic", "logo": "https://logo.clearbit.com/anthropic.com", "url": "https://anthropic.com/careers"},
        {"name": "Google DeepMind", "logo": "https://logo.clearbit.com/deepmind.com", "url": "https://deepmind.google/careers"},
        {"name": "Meta AI", "logo": "https://logo.clearbit.com/meta.com", "url": "https://metacareers.com"},
        {"name": "Microsoft", "logo": "https://logo.clearbit.com/microsoft.com", "url": "https://careers.microsoft.com"},
        {"name": "NVIDIA", "logo": "https://logo.clearbit.com/nvidia.com", "url": "https://nvidia.com/careers"},
        {"name": "Amazon AWS", "logo": "https://logo.clearbit.com/aws.amazon.com", "url": "https://amazon.jobs"},
        {"name": "Hugging Face", "logo": "https://logo.clearbit.com/huggingface.co", "url": "https://huggingface.co/jobs"},
        {"name": "Cohere", "logo": "https://logo.clearbit.com/cohere.com", "url": "https://cohere.com/careers"},
        {"name": "Mistral AI", "logo": "https://logo.clearbit.com/mistral.ai", "url": "https://mistral.ai/careers"},
        {"name": "Scale AI", "logo": "https://logo.clearbit.com/scale.com", "url": "https://scale.com/careers"},
        {"name": "Databricks", "logo": "https://logo.clearbit.com/databricks.com", "url": "https://databricks.com/careers"},
        {"name": "Stripe", "logo": "https://logo.clearbit.com/stripe.com", "url": "https://stripe.com/jobs"},
        {"name": "Airbnb", "logo": "https://logo.clearbit.com/airbnb.com", "url": "https://careers.airbnb.com"},
        {"name": "Netflix", "logo": "https://logo.clearbit.com/netflix.com", "url": "https://jobs.netflix.com"},
    ]

    # Job templates
    JOB_TEMPLATES = [
        {
            "title": "Senior Machine Learning Engineer",
            "description": "Design and implement scalable ML systems. Work on cutting-edge deep learning models for production deployment. Collaborate with research teams to bring innovations to market.",
            "requirements": ["5+ years ML experience", "Python, PyTorch/TensorFlow", "MLOps experience", "Strong mathematics background"],
            "job_type": "full_time",
            "experience_level": "Senior",
            "salary_min": 180000,
            "salary_max": 280000,
            "skills": ["Python", "PyTorch", "TensorFlow", "Kubernetes", "MLOps"],
        },
        {
            "title": "AI Research Scientist",
            "description": "Conduct fundamental research in machine learning and artificial intelligence. Publish papers at top venues like NeurIPS, ICML, and ICLR. Advance the state of the art in AI.",
            "requirements": ["PhD in ML/AI/CS", "Publication track record", "Deep expertise in a research area", "Strong coding skills"],
            "job_type": "full_time",
            "experience_level": "Senior",
            "salary_min": 200000,
            "salary_max": 350000,
            "skills": ["Deep Learning", "NLP", "Computer Vision", "Reinforcement Learning", "Research"],
        },
        {
            "title": "LLM Engineer",
            "description": "Build and optimize large language model applications. Fine-tune foundation models for specific use cases. Implement RAG systems and AI agents.",
            "requirements": ["3+ years in NLP/LLMs", "Experience with transformers", "LangChain/LlamaIndex knowledge", "Production LLM deployment"],
            "job_type": "full_time",
            "experience_level": "Mid-Level",
            "salary_min": 150000,
            "salary_max": 220000,
            "skills": ["LLMs", "LangChain", "Python", "RAG", "Prompt Engineering"],
        },
        {
            "title": "Computer Vision Engineer",
            "description": "Develop state-of-the-art computer vision systems. Work on object detection, segmentation, and image generation. Deploy models for real-time inference.",
            "requirements": ["3+ years CV experience", "Deep learning frameworks", "Image processing expertise", "C++/Python proficiency"],
            "job_type": "full_time",
            "experience_level": "Mid-Level",
            "salary_min": 140000,
            "salary_max": 200000,
            "skills": ["Computer Vision", "PyTorch", "OpenCV", "CUDA", "Deep Learning"],
        },
        {
            "title": "ML Platform Engineer",
            "description": "Build and maintain ML infrastructure at scale. Design feature stores, model registries, and training pipelines. Enable data scientists to deploy models efficiently.",
            "requirements": ["5+ years infrastructure experience", "Kubernetes/Docker expertise", "ML workflow tools", "Cloud platforms"],
            "job_type": "full_time",
            "experience_level": "Senior",
            "salary_min": 170000,
            "salary_max": 250000,
            "skills": ["Kubernetes", "Docker", "MLflow", "AWS/GCP", "Python"],
        },
        {
            "title": "AI Product Manager",
            "description": "Define product strategy for AI-powered features. Work with engineering and research teams to ship AI products. Understand market needs and translate them into requirements.",
            "requirements": ["5+ years PM experience", "Technical background", "AI/ML product experience", "Strong communication"],
            "job_type": "full_time",
            "experience_level": "Senior",
            "salary_min": 160000,
            "salary_max": 240000,
            "skills": ["Product Management", "AI/ML", "Strategy", "Analytics", "Leadership"],
        },
        {
            "title": "Data Scientist - NLP",
            "description": "Apply NLP techniques to solve business problems. Build text classification, sentiment analysis, and entity extraction systems. Work closely with product teams.",
            "requirements": ["3+ years data science", "NLP experience", "Python/SQL proficiency", "Statistics background"],
            "job_type": "full_time",
            "experience_level": "Mid-Level",
            "salary_min": 130000,
            "salary_max": 180000,
            "skills": ["NLP", "Python", "SQL", "Machine Learning", "Statistics"],
        },
        {
            "title": "Applied AI Engineer",
            "description": "Take AI research and apply it to real-world products. Bridge the gap between research and production. Build robust AI systems that scale.",
            "requirements": ["4+ years engineering", "ML systems experience", "Production deployment", "Full-stack capabilities"],
            "job_type": "full_time",
            "experience_level": "Senior",
            "salary_min": 160000,
            "salary_max": 230000,
            "skills": ["Machine Learning", "Software Engineering", "Python", "Cloud", "APIs"],
        },
        {
            "title": "ML Engineer - Recommendation Systems",
            "description": "Build personalization and recommendation systems at scale. Design collaborative filtering and content-based models. A/B test and optimize for business metrics.",
            "requirements": ["3+ years RecSys experience", "Deep learning for recommendations", "Large-scale systems", "Experimentation"],
            "job_type": "full_time",
            "experience_level": "Mid-Level",
            "salary_min": 150000,
            "salary_max": 210000,
            "skills": ["Recommendation Systems", "Deep Learning", "Python", "Spark", "A/B Testing"],
        },
        {
            "title": "AI Safety Researcher",
            "description": "Research AI alignment and safety. Develop techniques for interpretability and robustness. Help ensure AI systems are beneficial and safe.",
            "requirements": ["PhD or equivalent", "AI safety research", "Strong technical skills", "Publication record"],
            "job_type": "full_time",
            "experience_level": "Senior",
            "salary_min": 180000,
            "salary_max": 300000,
            "skills": ["AI Safety", "Alignment", "Interpretability", "Research", "Machine Learning"],
        },
    ]

    LOCATIONS = [
        {"city": "San Francisco", "state": "CA", "country": "USA", "is_remote": False},
        {"city": "New York", "state": "NY", "country": "USA", "is_remote": False},
        {"city": "Seattle", "state": "WA", "country": "USA", "is_remote": False},
        {"city": "London", "state": None, "country": "UK", "is_remote": False},
        {"city": "Toronto", "state": "ON", "country": "Canada", "is_remote": False},
        {"city": "Paris", "state": None, "country": "France", "is_remote": False},
        {"city": None, "state": None, "country": None, "is_remote": True},  # Remote
    ]

    def __init__(self):
        super().__init__("ai_jobs")

    async def collect(self, **kwargs) -> List[Dict[str, Any]]:
        """Generate curated AI job listings."""
        jobs = []
        job_id = 1000

        for company in self.AI_COMPANIES:
            # Each company has 2-4 jobs
            num_jobs = random.randint(2, 4)
            selected_templates = random.sample(self.JOB_TEMPLATES, min(num_jobs, len(self.JOB_TEMPLATES)))

            for template in selected_templates:
                location = random.choice(self.LOCATIONS)
                days_ago = random.randint(1, 30)

                job = {
                    "id": job_id,
                    "company": company,
                    "template": template,
                    "location": location,
                    "posted_days_ago": days_ago,
                }
                jobs.append(job)
                job_id += 1

        return jobs

    async def transform(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform job data to Job model format."""
        jobs = []

        for item in raw_data:
            company = item["company"]
            template = item["template"]
            location = item["location"]

            # Build location string
            loc_parts = []
            if location["city"]:
                loc_parts.append(location["city"])
            if location["state"]:
                loc_parts.append(location["state"])
            if location["country"]:
                loc_parts.append(location["country"])
            location_str = ", ".join(loc_parts) if loc_parts else "Remote"

            posted_at = datetime.now() - timedelta(days=item["posted_days_ago"])

            job = {
                "external_id": f"curated_{item['id']}",
                "source": "curated",
                "title": template["title"],
                "slug": self._create_slug(template["title"], company["name"], item["id"]),
                "description": template["description"],
                "requirements": template.get("requirements", []),
                "company_name": company["name"],
                "company_logo": company.get("logo"),
                "company_url": company.get("url"),
                "location": location_str,
                "city": location.get("city"),
                "state": location.get("state"),
                "country": location.get("country"),
                "is_remote": location["is_remote"],
                "job_type": template.get("job_type", "full_time"),
                "experience_level": template.get("experience_level"),
                "salary_min": template.get("salary_min"),
                "salary_max": template.get("salary_max"),
                "salary_currency": "USD",
                "skills": template.get("skills", []),
                "benefits": ["Health Insurance", "401k", "Stock Options", "Flexible PTO", "Remote Work"],
                "apply_url": company["url"],
                "source_url": company["url"],
                "posted_at": posted_at,
                "is_active": True,
                "is_featured": company["name"] in ["OpenAI", "Anthropic", "Google DeepMind"],
            }
            jobs.append(job)

        return jobs

    def _create_slug(self, title: str, company: str, job_id: int) -> str:
        """Create URL-friendly slug."""
        slug = f"{title} {company}".lower()
        slug = re.sub(r"[^a-z0-9\s-]", "", slug)
        slug = re.sub(r"[\s_]+", "-", slug)
        slug = re.sub(r"-+", "-", slug)
        return f"{slug.strip('-')[:100]}-{job_id}"
