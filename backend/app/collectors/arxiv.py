"""arXiv collector for research papers."""
from typing import Any, Dict, List, Optional
from datetime import datetime
import re
import feedparser
from .base import BaseCollector


class ArxivCollector(BaseCollector):
    """Collector for arXiv API."""

    BASE_URL = "http://export.arxiv.org/api/query"

    # AI-related categories
    AI_CATEGORIES = [
        "cs.AI",   # Artificial Intelligence
        "cs.LG",   # Machine Learning
        "cs.CL",   # Computation and Language (NLP)
        "cs.CV",   # Computer Vision
        "cs.NE",   # Neural and Evolutionary Computing
        "stat.ML", # Machine Learning (Statistics)
    ]

    def __init__(self):
        super().__init__("arxiv")

    async def collect(
        self,
        categories: Optional[List[str]] = None,
        max_results: int = 100,
        search_query: Optional[str] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Collect papers from arXiv."""
        cats = categories or self.AI_CATEGORIES

        # Build query
        if search_query:
            query = f"all:{search_query}"
        else:
            cat_query = " OR ".join([f"cat:{cat}" for cat in cats])
            query = f"({cat_query})"

        params = {
            "search_query": query,
            "start": 0,
            "max_results": max_results,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }

        try:
            response = await self.fetch_url(self.BASE_URL, params=params)
            feed = feedparser.parse(response.text)
            return feed.entries
        except Exception as e:
            self.logger.error(f"Error fetching from arXiv: {e}")
            return []

    async def transform(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform arXiv data to research paper model format."""
        papers = []

        for entry in raw_data:
            # Extract arXiv ID from entry ID URL
            arxiv_id = self._extract_arxiv_id(entry.get("id", ""))

            # Extract categories
            categories = [tag.get("term") for tag in entry.get("tags", [])]
            primary_category = categories[0] if categories else None

            # Parse dates
            published_at = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                try:
                    published_at = datetime(*entry.published_parsed[:6])
                except Exception:
                    pass

            updated_at = None
            if hasattr(entry, "updated_parsed") and entry.updated_parsed:
                try:
                    updated_at = datetime(*entry.updated_parsed[:6])
                except Exception:
                    pass

            # Extract authors
            authors = []
            for author in entry.get("authors", []):
                author_data = {
                    "name": author.get("name", ""),
                    "affiliation": None,
                }
                if hasattr(author, "arxiv_affiliation"):
                    author_data["affiliation"] = author.arxiv_affiliation
                authors.append(author_data)

            # Build URLs
            paper_url = entry.get("link", "")
            pdf_url = None
            for link in entry.get("links", []):
                if link.get("type") == "application/pdf":
                    pdf_url = link.get("href")
                    break

            paper = {
                "external_id": arxiv_id,
                "source": "arxiv",
                "title": entry.get("title", "").replace("\n", " ").strip(),
                "slug": self._create_slug(entry.get("title", "")),
                "abstract": entry.get("summary", "").replace("\n", " ").strip(),
                "arxiv_id": arxiv_id,
                "doi": entry.get("arxiv_doi"),
                "pdf_url": pdf_url,
                "paper_url": paper_url,
                "primary_category": primary_category,
                "categories": categories,
                "published_at": published_at,
                "updated_at_source": updated_at,
                "extra_data": {
                    "authors": authors,
                    "comment": entry.get("arxiv_comment"),
                    "journal_ref": entry.get("arxiv_journal_ref"),
                },
            }
            papers.append(paper)

        return papers

    def _extract_arxiv_id(self, url: str) -> str:
        """Extract arXiv ID from URL."""
        # URL format: http://arxiv.org/abs/2312.12345v1
        match = re.search(r"arxiv\.org/abs/(.+?)(?:v\d+)?$", url)
        if match:
            return match.group(1)
        return url.split("/")[-1]

    def _create_slug(self, title: str) -> str:
        """Create URL-friendly slug from title."""
        slug = title.lower()
        slug = re.sub(r"[^a-z0-9\s-]", "", slug)
        slug = re.sub(r"[\s_]+", "-", slug)
        slug = re.sub(r"-+", "-", slug)
        return slug.strip("-")[:550]
