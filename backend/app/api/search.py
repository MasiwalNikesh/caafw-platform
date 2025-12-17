"""Global search API endpoint."""
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, union_all, literal_column
from pydantic import BaseModel

from app.db.database import get_db
from app.models.product import Product
from app.models.job import Job
from app.models.news import NewsArticle
from app.models.research import ResearchPaper
from app.models.mcp_server import MCPServer

router = APIRouter()


class SearchResult(BaseModel):
    """Search result item."""
    id: int
    type: str
    title: str
    description: Optional[str] = None
    url: Optional[str] = None
    image_url: Optional[str] = None


class SearchResponse(BaseModel):
    """Search response with results grouped by type."""
    query: str
    total: int
    results: List[SearchResult]
    by_type: Dict[str, int]


@router.get("", response_model=SearchResponse)
async def global_search(
    q: str = Query(..., min_length=2, description="Search query"),
    types: Optional[str] = Query(
        default=None,
        description="Comma-separated list of types to search (products,jobs,news,research,mcp)"
    ),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """
    Global search across all content types.

    Search for products, jobs, news articles, research papers, and MCP servers
    in a single query.
    """
    search_term = f"%{q}%"
    results: List[SearchResult] = []
    by_type: Dict[str, int] = {}

    # Determine which types to search
    types_to_search = (
        types.split(",") if types
        else ["products", "jobs", "news", "research", "mcp"]
    )

    # Search Products
    if "products" in types_to_search:
        product_query = (
            select(
                Product.id,
                Product.name.label("title"),
                Product.tagline.label("description"),
                Product.website_url.label("url"),
                Product.logo_url.label("image_url"),
            )
            .where(
                Product.is_active == True,
                (Product.name.ilike(search_term) |
                 Product.tagline.ilike(search_term) |
                 Product.description.ilike(search_term))
            )
            .limit(limit)
        )
        result = await db.execute(product_query)
        products = result.all()
        by_type["products"] = len(products)
        for p in products:
            results.append(SearchResult(
                id=p.id,
                type="product",
                title=p.title,
                description=p.description,
                url=p.url,
                image_url=p.image_url,
            ))

    # Search Jobs
    if "jobs" in types_to_search:
        job_query = (
            select(
                Job.id,
                Job.title,
                Job.company_name.label("description"),
                Job.apply_url.label("url"),
                Job.company_logo.label("image_url"),
            )
            .where(
                Job.is_active == True,
                (Job.title.ilike(search_term) |
                 Job.description.ilike(search_term) |
                 Job.company_name.ilike(search_term))
            )
            .limit(limit)
        )
        result = await db.execute(job_query)
        jobs = result.all()
        by_type["jobs"] = len(jobs)
        for j in jobs:
            results.append(SearchResult(
                id=j.id,
                type="job",
                title=j.title,
                description=j.description,
                url=j.url,
                image_url=j.image_url,
            ))

    # Search News
    if "news" in types_to_search:
        news_query = (
            select(
                NewsArticle.id,
                NewsArticle.title,
                NewsArticle.summary.label("description"),
                NewsArticle.url,
                NewsArticle.image_url,
            )
            .where(
                NewsArticle.is_active == True,
                (NewsArticle.title.ilike(search_term) |
                 NewsArticle.summary.ilike(search_term))
            )
            .limit(limit)
        )
        result = await db.execute(news_query)
        news = result.all()
        by_type["news"] = len(news)
        for n in news:
            results.append(SearchResult(
                id=n.id,
                type="news",
                title=n.title,
                description=n.description,
                url=n.url,
                image_url=n.image_url,
            ))

    # Search Research Papers
    if "research" in types_to_search:
        research_query = (
            select(
                ResearchPaper.id,
                ResearchPaper.title,
                ResearchPaper.abstract.label("description"),
                ResearchPaper.paper_url.label("url"),
            )
            .where(
                ResearchPaper.title.ilike(search_term) |
                ResearchPaper.abstract.ilike(search_term)
            )
            .limit(limit)
        )
        result = await db.execute(research_query)
        papers = result.all()
        by_type["research"] = len(papers)
        for p in papers:
            results.append(SearchResult(
                id=p.id,
                type="research",
                title=p.title,
                description=p.description[:200] + "..." if p.description and len(p.description) > 200 else p.description,
                url=p.url,
                image_url=None,
            ))

    # Search MCP Servers
    if "mcp" in types_to_search:
        mcp_query = (
            select(
                MCPServer.id,
                MCPServer.name.label("title"),
                MCPServer.short_description.label("description"),
                MCPServer.repository_url.label("url"),
            )
            .where(
                MCPServer.is_active == True,
                (MCPServer.name.ilike(search_term) |
                 MCPServer.description.ilike(search_term))
            )
            .limit(limit)
        )
        result = await db.execute(mcp_query)
        servers = result.all()
        by_type["mcp"] = len(servers)
        for s in servers:
            results.append(SearchResult(
                id=s.id,
                type="mcp",
                title=s.title,
                description=s.description,
                url=s.url,
                image_url=None,
            ))

    return SearchResponse(
        query=q,
        total=len(results),
        results=results[:limit],
        by_type=by_type,
    )
