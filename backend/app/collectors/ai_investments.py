"""AI Investments collector with curated AI company funding data."""
from typing import Any, Dict, List, Optional
from datetime import datetime
import re
from .base import BaseCollector


class AIInvestmentsCollector(BaseCollector):
    """Collector for AI company investment and funding data."""

    # Major AI companies with funding data (curated from public sources)
    AI_COMPANIES = [
        {
            "name": "OpenAI",
            "description": "OpenAI is an AI research and deployment company. Our mission is to ensure that artificial general intelligence benefits all of humanity. Creators of GPT-4, ChatGPT, DALL-E, and Sora.",
            "website_url": "https://openai.com",
            "logo_url": "https://upload.wikimedia.org/wikipedia/commons/4/4d/OpenAI_Logo.svg",
            "city": "San Francisco",
            "country": "USA",
            "founded_year": 2015,
            "employee_count": "1001-5000",
            "total_funding": 11300000000,
            "funding_status": "series_d",
            "valuation": 86000000000,
            "industries": ["Artificial Intelligence", "Machine Learning", "Research"],
            "categories": ["LLM", "Generative AI", "AGI Research"],
            "lead_investors": ["Microsoft", "Thrive Capital", "Sequoia Capital", "a16z"],
            "is_featured": True,
            "funding_rounds": [
                {"round_type": "Series A", "amount": 1000000000, "announced_at": "2019-07-22", "lead_investors": ["Microsoft"]},
                {"round_type": "Series B", "amount": 2000000000, "announced_at": "2021-01-01", "lead_investors": ["Microsoft"]},
                {"round_type": "Series C", "amount": 10000000000, "announced_at": "2023-01-23", "lead_investors": ["Microsoft"]},
                {"round_type": "Series D", "amount": 6600000000, "announced_at": "2024-10-02", "lead_investors": ["Thrive Capital", "Microsoft"]},
            ],
        },
        {
            "name": "Anthropic",
            "description": "Anthropic is an AI safety company working to build reliable, interpretable, and steerable AI systems. Creators of Claude, a helpful, harmless, and honest AI assistant.",
            "website_url": "https://anthropic.com",
            "logo_url": "https://anthropic.com/images/icons/apple-touch-icon.png",
            "city": "San Francisco",
            "country": "USA",
            "founded_year": 2021,
            "employee_count": "501-1000",
            "total_funding": 7300000000,
            "funding_status": "series_d",
            "valuation": 18000000000,
            "industries": ["Artificial Intelligence", "AI Safety", "Research"],
            "categories": ["LLM", "AI Safety", "Enterprise AI"],
            "lead_investors": ["Google", "Spark Capital", "Salesforce Ventures", "Amazon"],
            "is_featured": True,
            "funding_rounds": [
                {"round_type": "Series A", "amount": 124000000, "announced_at": "2022-04-01", "lead_investors": ["Spark Capital"]},
                {"round_type": "Series B", "amount": 580000000, "announced_at": "2023-02-01", "lead_investors": ["Spark Capital", "Google"]},
                {"round_type": "Series C", "amount": 450000000, "announced_at": "2023-05-23", "lead_investors": ["Spark Capital"]},
                {"round_type": "Series D", "amount": 2000000000, "announced_at": "2023-09-25", "lead_investors": ["Google"]},
                {"round_type": "Series E", "amount": 4000000000, "announced_at": "2024-03-27", "lead_investors": ["Amazon"]},
            ],
        },
        {
            "name": "Mistral AI",
            "description": "Mistral AI is a French AI company developing open and portable generative AI models. Known for Mixtral and Mistral models that compete with larger models at lower costs.",
            "website_url": "https://mistral.ai",
            "logo_url": "https://mistral.ai/images/logo.svg",
            "city": "Paris",
            "country": "France",
            "founded_year": 2023,
            "employee_count": "51-100",
            "total_funding": 1000000000,
            "funding_status": "series_b",
            "valuation": 6000000000,
            "industries": ["Artificial Intelligence", "Open Source AI"],
            "categories": ["LLM", "Open Source", "Enterprise AI"],
            "lead_investors": ["Andreessen Horowitz", "Lightspeed", "General Catalyst"],
            "is_featured": True,
            "funding_rounds": [
                {"round_type": "Seed", "amount": 113000000, "announced_at": "2023-06-13", "lead_investors": ["Lightspeed"]},
                {"round_type": "Series A", "amount": 415000000, "announced_at": "2023-12-11", "lead_investors": ["Andreessen Horowitz"]},
                {"round_type": "Series B", "amount": 640000000, "announced_at": "2024-06-11", "lead_investors": ["General Catalyst"]},
            ],
        },
        {
            "name": "Cohere",
            "description": "Cohere provides enterprise AI solutions with a focus on natural language processing. Their models power search, generation, and classification for businesses.",
            "website_url": "https://cohere.com",
            "logo_url": "https://cohere.com/favicon.ico",
            "city": "Toronto",
            "country": "Canada",
            "founded_year": 2019,
            "employee_count": "201-500",
            "total_funding": 970000000,
            "funding_status": "series_d",
            "valuation": 5500000000,
            "industries": ["Artificial Intelligence", "NLP", "Enterprise"],
            "categories": ["LLM", "Enterprise AI", "NLP"],
            "lead_investors": ["Inovia Capital", "NVIDIA", "Salesforce Ventures"],
            "is_featured": True,
            "funding_rounds": [
                {"round_type": "Seed", "amount": 40000000, "announced_at": "2021-09-08", "lead_investors": ["Radical Ventures"]},
                {"round_type": "Series B", "amount": 125000000, "announced_at": "2022-02-17", "lead_investors": ["Tiger Global"]},
                {"round_type": "Series C", "amount": 270000000, "announced_at": "2023-06-08", "lead_investors": ["Inovia Capital"]},
                {"round_type": "Series D", "amount": 500000000, "announced_at": "2024-07-22", "lead_investors": ["PSP Investments"]},
            ],
        },
        {
            "name": "Stability AI",
            "description": "Stability AI is the company behind Stable Diffusion, an open-source image generation model. They focus on democratizing AI through open models.",
            "website_url": "https://stability.ai",
            "logo_url": "https://stability.ai/favicon.ico",
            "city": "London",
            "country": "UK",
            "founded_year": 2020,
            "employee_count": "101-200",
            "total_funding": 173000000,
            "funding_status": "series_a",
            "valuation": 1000000000,
            "industries": ["Artificial Intelligence", "Generative AI", "Open Source"],
            "categories": ["Image Generation", "Open Source", "Generative AI"],
            "lead_investors": ["Coatue", "Lightspeed"],
            "is_featured": True,
            "funding_rounds": [
                {"round_type": "Seed", "amount": 100000000, "announced_at": "2022-10-17", "lead_investors": ["Coatue", "Lightspeed"]},
            ],
        },
        {
            "name": "Hugging Face",
            "description": "Hugging Face is the collaboration platform for the machine learning community. They host models, datasets, and provide tools for ML development.",
            "website_url": "https://huggingface.co",
            "logo_url": "https://huggingface.co/front/assets/huggingface_logo.svg",
            "city": "New York",
            "country": "USA",
            "founded_year": 2016,
            "employee_count": "201-500",
            "total_funding": 395000000,
            "funding_status": "series_d",
            "valuation": 4500000000,
            "industries": ["Artificial Intelligence", "Developer Tools", "Open Source"],
            "categories": ["ML Platform", "Open Source", "Developer Tools"],
            "lead_investors": ["Lux Capital", "Salesforce Ventures", "Google"],
            "is_featured": True,
            "funding_rounds": [
                {"round_type": "Series C", "amount": 100000000, "announced_at": "2022-05-09", "lead_investors": ["Lux Capital"]},
                {"round_type": "Series D", "amount": 235000000, "announced_at": "2023-08-24", "lead_investors": ["Salesforce Ventures", "Google"]},
            ],
        },
        {
            "name": "Runway",
            "description": "Runway is an applied AI research company building the next generation of creative tools. Known for Gen-2 video generation and AI-powered creative software.",
            "website_url": "https://runway.ml",
            "logo_url": "https://runway.ml/favicon.ico",
            "city": "New York",
            "country": "USA",
            "founded_year": 2018,
            "employee_count": "101-200",
            "total_funding": 237000000,
            "funding_status": "series_c",
            "valuation": 1500000000,
            "industries": ["Artificial Intelligence", "Creative Tools", "Video"],
            "categories": ["Video Generation", "Creative AI", "Generative AI"],
            "lead_investors": ["Felicis Ventures", "Coatue", "Lux Capital"],
            "is_featured": True,
            "funding_rounds": [
                {"round_type": "Series B", "amount": 50000000, "announced_at": "2022-12-05", "lead_investors": ["Felicis Ventures"]},
                {"round_type": "Series C", "amount": 141000000, "announced_at": "2023-06-29", "lead_investors": ["Spark Capital"]},
            ],
        },
        {
            "name": "Perplexity AI",
            "description": "Perplexity AI is building an AI-powered answer engine that provides direct answers to questions using the latest information from the internet.",
            "website_url": "https://perplexity.ai",
            "logo_url": "https://perplexity.ai/favicon.ico",
            "city": "San Francisco",
            "country": "USA",
            "founded_year": 2022,
            "employee_count": "51-100",
            "total_funding": 165000000,
            "funding_status": "series_b",
            "valuation": 3000000000,
            "industries": ["Artificial Intelligence", "Search", "Information Retrieval"],
            "categories": ["AI Search", "LLM Applications", "Consumer AI"],
            "lead_investors": ["IVP", "NEA", "Databricks Ventures"],
            "is_featured": True,
            "funding_rounds": [
                {"round_type": "Series A", "amount": 25600000, "announced_at": "2023-03-23", "lead_investors": ["NEA"]},
                {"round_type": "Series B", "amount": 73600000, "announced_at": "2024-01-04", "lead_investors": ["IVP"]},
            ],
        },
        {
            "name": "Scale AI",
            "description": "Scale AI provides high-quality training data for AI applications. Their platform combines human intelligence with machine learning.",
            "website_url": "https://scale.com",
            "logo_url": "https://scale.com/favicon.ico",
            "city": "San Francisco",
            "country": "USA",
            "founded_year": 2016,
            "employee_count": "501-1000",
            "total_funding": 600000000,
            "funding_status": "series_e",
            "valuation": 7300000000,
            "industries": ["Artificial Intelligence", "Data Labeling", "MLOps"],
            "categories": ["Data Platform", "ML Infrastructure", "Enterprise AI"],
            "lead_investors": ["Tiger Global", "Index Ventures", "Accel"],
            "is_featured": True,
            "funding_rounds": [
                {"round_type": "Series D", "amount": 155000000, "announced_at": "2021-04-13", "lead_investors": ["Tiger Global"]},
                {"round_type": "Series E", "amount": 325000000, "announced_at": "2021-08-05", "lead_investors": ["Tiger Global"]},
            ],
        },
        {
            "name": "Inflection AI",
            "description": "Inflection AI built Pi, a personal AI assistant focused on emotional intelligence and helpful conversation. The company was acquired and team joined Microsoft.",
            "website_url": "https://inflection.ai",
            "logo_url": "https://inflection.ai/favicon.ico",
            "city": "Palo Alto",
            "country": "USA",
            "founded_year": 2022,
            "employee_count": "51-100",
            "total_funding": 1525000000,
            "funding_status": "series_b",
            "valuation": 4000000000,
            "industries": ["Artificial Intelligence", "Consumer AI", "Conversational AI"],
            "categories": ["Personal AI", "LLM", "Consumer AI"],
            "lead_investors": ["Microsoft", "NVIDIA", "Reid Hoffman"],
            "is_featured": False,
            "funding_rounds": [
                {"round_type": "Series A", "amount": 225000000, "announced_at": "2022-05-13", "lead_investors": ["Greylock"]},
                {"round_type": "Series B", "amount": 1300000000, "announced_at": "2023-06-29", "lead_investors": ["Microsoft", "NVIDIA"]},
            ],
        },
        {
            "name": "Databricks",
            "description": "Databricks provides a unified analytics platform for data engineering, data science, and machine learning. Known for their Lakehouse architecture and MLflow.",
            "website_url": "https://databricks.com",
            "logo_url": "https://databricks.com/favicon.ico",
            "city": "San Francisco",
            "country": "USA",
            "founded_year": 2013,
            "employee_count": "5001-10000",
            "total_funding": 4100000000,
            "funding_status": "series_i",
            "valuation": 43000000000,
            "industries": ["Data Analytics", "Machine Learning", "Cloud"],
            "categories": ["Data Platform", "ML Platform", "Enterprise"],
            "lead_investors": ["Andreessen Horowitz", "T. Rowe Price", "NEA"],
            "is_featured": True,
            "funding_rounds": [
                {"round_type": "Series G", "amount": 1000000000, "announced_at": "2021-02-01", "lead_investors": ["Franklin Templeton"]},
                {"round_type": "Series H", "amount": 1600000000, "announced_at": "2021-08-31", "lead_investors": ["Morgan Stanley"]},
                {"round_type": "Series I", "amount": 500000000, "announced_at": "2023-09-14", "lead_investors": ["T. Rowe Price"]},
            ],
        },
        {
            "name": "Adept AI",
            "description": "Adept AI is building AI that can take actions in software. Their models are designed to interact with any software interface.",
            "website_url": "https://adept.ai",
            "logo_url": "https://adept.ai/favicon.ico",
            "city": "San Francisco",
            "country": "USA",
            "founded_year": 2022,
            "employee_count": "51-100",
            "total_funding": 415000000,
            "funding_status": "series_b",
            "valuation": 1000000000,
            "industries": ["Artificial Intelligence", "Automation", "Enterprise"],
            "categories": ["AI Agents", "Automation", "Enterprise AI"],
            "lead_investors": ["General Catalyst", "Spark Capital"],
            "is_featured": False,
            "funding_rounds": [
                {"round_type": "Series A", "amount": 65000000, "announced_at": "2022-04-26", "lead_investors": ["Greylock"]},
                {"round_type": "Series B", "amount": 350000000, "announced_at": "2023-03-14", "lead_investors": ["General Catalyst", "Spark Capital"]},
            ],
        },
    ]

    def __init__(self):
        super().__init__("ai_investments")

    async def collect(self, **kwargs) -> List[Dict[str, Any]]:
        """Collect AI company and funding data."""
        return self.AI_COMPANIES

    async def transform(self, raw_data: List[Dict[str, Any]]) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Transform data to Company and FundingRound model formats."""
        companies = []
        funding_rounds = []

        for item in raw_data:
            slug = self._create_slug(item.get("name", ""))

            company = {
                "external_id": f"curated_{slug}",
                "source": "curated",
                "name": item.get("name"),
                "slug": slug,
                "description": item.get("description"),
                "short_description": (item.get("description", "") or "")[:200],
                "website_url": item.get("website_url"),
                "logo_url": item.get("logo_url"),
                "city": item.get("city"),
                "country": item.get("country"),
                "founded_year": item.get("founded_year"),
                "employee_count": item.get("employee_count"),
                "total_funding": item.get("total_funding"),
                "funding_status": item.get("funding_status"),
                "valuation": item.get("valuation"),
                "industries": item.get("industries", []),
                "categories": item.get("categories", []),
                "lead_investors": item.get("lead_investors", []),
                "num_investors": len(item.get("lead_investors", [])),
                "is_ai_company": True,
                "is_featured": item.get("is_featured", False),
                "is_active": True,
            }
            companies.append(company)

            # Process funding rounds
            for round_data in item.get("funding_rounds", []):
                funding_round = {
                    "external_id": f"curated_{slug}_{round_data.get('round_type', '').lower().replace(' ', '_')}",
                    "round_type": round_data.get("round_type"),
                    "amount": round_data.get("amount"),
                    "currency": "USD",
                    "lead_investors": round_data.get("lead_investors", []),
                    "num_investors": len(round_data.get("lead_investors", [])),
                    "announced_at": self._parse_date(round_data.get("announced_at")),
                    "_company_slug": slug,
                }
                funding_rounds.append(funding_round)

        return companies, funding_rounds

    def _create_slug(self, name: str) -> str:
        """Create URL-friendly slug from name."""
        slug = name.lower()
        slug = re.sub(r"[^a-z0-9\s-]", "", slug)
        slug = re.sub(r"[\s_]+", "-", slug)
        slug = re.sub(r"-+", "-", slug)
        return slug.strip("-")

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string."""
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except (ValueError, TypeError):
            return None
