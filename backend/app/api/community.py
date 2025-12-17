"""Community content API endpoints (Hacker News, Reddit, GitHub, Twitter)."""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.database import get_db, AsyncSessionLocal
from app.models.community import HackerNewsItem, RedditPost, GitHubRepo, Tweet
from app.schemas.community import (
    HackerNewsResponse,
    HackerNewsListResponse,
    RedditPostResponse,
    RedditListResponse,
    GitHubRepoResponse,
    GitHubListResponse,
    TweetResponse,
    TweetListResponse,
)
from app.collectors.ai_social import AISocialCollector
from app.collectors.github import GitHubCollector
from app.collectors.hackernews import HackerNewsCollector

router = APIRouter()


# Hacker News endpoints
@router.get("/hackernews", response_model=HackerNewsListResponse)
async def list_hackernews(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    item_type: str = Query(default="story"),
    search: Optional[str] = None,
    sort_by: str = Query(default="score", pattern="^(score|posted_at|comments_count)$"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db),
):
    """List Hacker News items."""
    query = select(HackerNewsItem).where(
        HackerNewsItem.item_type == item_type,
        HackerNewsItem.is_dead == False,
        HackerNewsItem.is_deleted == False,
    )

    if search:
        query = query.where(HackerNewsItem.title.ilike(f"%{search}%"))

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    # Apply sorting
    sort_column = getattr(HackerNewsItem, sort_by)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc().nullslast())
    else:
        query = query.order_by(sort_column.asc().nullsfirst())

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    items = result.scalars().all()

    total_pages = (total + page_size - 1) // page_size

    return HackerNewsListResponse(
        items=[HackerNewsResponse.model_validate(i) for i in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )


@router.get("/hackernews/{item_id}", response_model=HackerNewsResponse)
async def get_hackernews_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a single Hacker News item."""
    query = select(HackerNewsItem).where(HackerNewsItem.id == item_id)
    result = await db.execute(query)
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    return HackerNewsResponse.model_validate(item)


# Reddit endpoints
@router.get("/reddit", response_model=RedditListResponse)
async def list_reddit_posts(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    subreddit: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = Query(default="score", pattern="^(score|posted_at|num_comments)$"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db),
):
    """List Reddit posts."""
    query = select(RedditPost)

    if subreddit:
        query = query.where(RedditPost.subreddit == subreddit)
    if search:
        query = query.where(
            RedditPost.title.ilike(f"%{search}%") |
            RedditPost.selftext.ilike(f"%{search}%")
        )

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    # Apply sorting
    sort_column = getattr(RedditPost, sort_by)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc().nullslast())
    else:
        query = query.order_by(sort_column.asc().nullsfirst())

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    posts = result.scalars().all()

    total_pages = (total + page_size - 1) // page_size

    return RedditListResponse(
        items=[RedditPostResponse.model_validate(p) for p in posts],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )


# GitHub endpoints
@router.get("/github", response_model=GitHubListResponse)
async def list_github_repos(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    language: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = Query(default="stars", pattern="^(stars|forks|repo_updated_at)$"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db),
):
    """List GitHub repositories."""
    query = select(GitHubRepo).where(GitHubRepo.is_archived == False)

    if language:
        query = query.where(GitHubRepo.language == language)
    if search:
        query = query.where(
            GitHubRepo.name.ilike(f"%{search}%") |
            GitHubRepo.description.ilike(f"%{search}%")
        )

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    # Apply sorting
    sort_column = getattr(GitHubRepo, sort_by)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc().nullslast())
    else:
        query = query.order_by(sort_column.asc().nullsfirst())

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    repos = result.scalars().all()

    total_pages = (total + page_size - 1) // page_size

    return GitHubListResponse(
        items=[GitHubRepoResponse.model_validate(r) for r in repos],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )


@router.get("/github/{repo_id}", response_model=GitHubRepoResponse)
async def get_github_repo(
    repo_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a single GitHub repository."""
    query = select(GitHubRepo).where(GitHubRepo.id == repo_id)
    result = await db.execute(query)
    repo = result.scalar_one_or_none()

    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    return GitHubRepoResponse.model_validate(repo)


# Twitter/X endpoints
@router.get("/tweets", response_model=TweetListResponse)
async def list_tweets(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    topic: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = Query(default="likes", pattern="^(likes|retweets|tweeted_at)$"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db),
):
    """List AI-related tweets."""
    query = select(Tweet)

    if topic:
        query = query.where(Tweet.topic == topic)
    if search:
        query = query.where(Tweet.text.ilike(f"%{search}%"))

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    # Apply sorting
    sort_column = getattr(Tweet, sort_by)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc().nullslast())
    else:
        query = query.order_by(sort_column.asc().nullsfirst())

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    tweets = result.scalars().all()

    total_pages = (total + page_size - 1) // page_size

    return TweetListResponse(
        items=[TweetResponse.model_validate(t) for t in tweets],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )


@router.get("/tweets/{tweet_id}", response_model=TweetResponse)
async def get_tweet(
    tweet_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a single tweet by ID."""
    query = select(Tweet).where(Tweet.id == tweet_id)
    result = await db.execute(query)
    tweet = result.scalar_one_or_none()

    if not tweet:
        raise HTTPException(status_code=404, detail="Tweet not found")

    return TweetResponse.model_validate(tweet)


@router.get("/tweets/topics/list")
async def get_tweet_topics():
    """Get available AI subreddits for social feed collection."""
    return {
        "topics": AISocialCollector.AI_SUBREDDITS,
        "description": "Available AI-related subreddits for content collection"
    }


@router.post("/tweets/collect", tags=["Collection"])
async def collect_tweets(
    subreddit: Optional[str] = Query(default=None, description="Specific subreddit to fetch from"),
    limit: int = Query(default=25, ge=10, le=50),
    sort: str = Query(default="hot", pattern="^(hot|new|top|rising)$"),
):
    """Collect AI-related content from Reddit as social feed."""
    collector = AISocialCollector()

    try:
        # Collect posts
        if subreddit:
            raw_data = await collector.collect(subreddits=[subreddit], limit=limit, sort=sort)
        else:
            # Default: collect from top AI subreddits
            raw_data = await collector.collect_trending(limit_per_sub=limit // 5 or 5)

        if not raw_data:
            return {"message": "No posts collected", "collected": 0, "inserted": 0}

        # Transform data
        transformed_data = await collector.transform(raw_data)

        # Upsert into database
        async with AsyncSessionLocal() as session:
            inserted = 0
            updated = 0

            for item in transformed_data:
                # Remove extra_data for DB insert (store separately if needed)
                item_copy = {k: v for k, v in item.items() if k != "extra_data"}

                # Check if exists
                db_query = select(Tweet).where(Tweet.tweet_id == item_copy.get("tweet_id"))
                result = await session.execute(db_query)
                existing = result.scalar_one_or_none()

                if existing:
                    # Update existing
                    for key, value in item_copy.items():
                        if hasattr(existing, key) and key != "id":
                            setattr(existing, key, value)
                    updated += 1
                else:
                    # Insert new
                    new_post = Tweet(**item_copy)
                    session.add(new_post)
                    inserted += 1

            await session.commit()

        return {
            "message": "Collection complete",
            "source": "reddit",
            "collected": len(transformed_data),
            "inserted": inserted,
            "updated": updated,
            "subreddit": subreddit,
            "sort": sort,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Collection failed: {str(e)}")


# GitHub Collection
@router.post("/github/collect", tags=["Collection"])
async def collect_github_repos(
    language: Optional[str] = Query(default=None, description="Filter by programming language"),
    limit: int = Query(default=50, ge=10, le=100),
):
    """Collect AI-related trending repositories from GitHub."""
    collector = GitHubCollector()

    try:
        # Collect repos using search method
        raw_data = await collector.collect(method="search", language=language, limit=limit)

        if not raw_data:
            return {"message": "No repositories collected", "collected": 0, "inserted": 0}

        # Transform data
        transformed_data = await collector.transform(raw_data)

        # Upsert into database
        async with AsyncSessionLocal() as session:
            inserted = 0
            updated = 0

            for item in transformed_data:
                # Check if exists by full_name
                db_query = select(GitHubRepo).where(GitHubRepo.full_name == item.get("full_name"))
                result = await session.execute(db_query)
                existing = result.scalar_one_or_none()

                if existing:
                    # Update existing
                    for key, value in item.items():
                        if hasattr(existing, key) and key != "id":
                            setattr(existing, key, value)
                    updated += 1
                else:
                    # Insert new
                    new_repo = GitHubRepo(**item)
                    session.add(new_repo)
                    inserted += 1

            await session.commit()

        return {
            "message": "Collection complete",
            "collected": len(transformed_data),
            "inserted": inserted,
            "updated": updated,
            "language": language,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Collection failed: {str(e)}")


# Hacker News Collection
@router.post("/hackernews/collect", tags=["Collection"])
async def collect_hackernews(
    limit: int = Query(default=50, ge=10, le=100),
    story_type: str = Query(default="top", pattern="^(top|best|new)$"),
):
    """Collect top stories from Hacker News."""
    collector = HackerNewsCollector()

    try:
        # Collect stories
        raw_data = await collector.collect(story_type=story_type, limit=limit)

        if not raw_data:
            return {"message": "No stories collected", "collected": 0, "inserted": 0}

        # Transform data
        transformed_data = await collector.transform(raw_data)

        # Upsert into database
        async with AsyncSessionLocal() as session:
            inserted = 0
            updated = 0

            for item in transformed_data:
                # Check if exists by hn_id
                db_query = select(HackerNewsItem).where(HackerNewsItem.hn_id == item.get("hn_id"))
                result = await session.execute(db_query)
                existing = result.scalar_one_or_none()

                if existing:
                    # Update existing
                    for key, value in item.items():
                        if hasattr(existing, key) and key != "id":
                            setattr(existing, key, value)
                    updated += 1
                else:
                    # Insert new
                    new_item = HackerNewsItem(**item)
                    session.add(new_item)
                    inserted += 1

            await session.commit()

        return {
            "message": "Collection complete",
            "collected": len(transformed_data),
            "inserted": inserted,
            "updated": updated,
            "story_type": story_type,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Collection failed: {str(e)}")
