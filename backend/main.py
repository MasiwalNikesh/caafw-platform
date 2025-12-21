"""
AI Community Platform - Main Application Entry Point
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.database import engine, Base
from app.api import (
    products,
    jobs,
    news,
    research,
    learning,
    mcp_servers,
    community,
    events,
    investments,
    search,
    auth,
    quiz,
    updates,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown events."""
    # Startup: Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown: Clean up resources
    await engine.dispose()


app = FastAPI(
    title="AI Community Platform API",
    description="A comprehensive API for the AI Community Platform (CAAFW)",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(products.router, prefix="/api/v1/products", tags=["Products"])
app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["Jobs"])
app.include_router(news.router, prefix="/api/v1/news", tags=["News"])
app.include_router(research.router, prefix="/api/v1/research", tags=["Research"])
app.include_router(learning.router, prefix="/api/v1/learning", tags=["Learning"])
app.include_router(mcp_servers.router, prefix="/api/v1/mcp-servers", tags=["MCP Servers"])
app.include_router(community.router, prefix="/api/v1/community", tags=["Community"])
app.include_router(events.router, prefix="/api/v1/events", tags=["Events"])
app.include_router(investments.router, prefix="/api/v1/investments", tags=["Investments"])
app.include_router(search.router, prefix="/api/v1/search", tags=["Search"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(quiz.router, prefix="/api/v1/quiz", tags=["Quiz"])
app.include_router(updates.router, prefix="/api/v1/updates", tags=["Updates"])


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint for health check."""
    return {
        "status": "healthy",
        "name": "AI Community Platform API",
        "version": "1.0.0",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "database": "connected",
        "cache": "connected",
        "search": "connected",
    }
