"""Community content models (Hacker News, Reddit, GitHub)."""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Text, Integer, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base
from .base import TimestampMixin


class HackerNewsItem(Base, TimestampMixin):
    """Hacker News item model."""

    __tablename__ = "hackernews_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    hn_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    item_type: Mapped[str] = mapped_column(String(20), nullable=False)  # story, comment, job, poll

    # Content
    title: Mapped[Optional[str]] = mapped_column(String(500))
    url: Mapped[Optional[str]] = mapped_column(String(500))
    text: Mapped[Optional[str]] = mapped_column(Text)

    # Author
    author: Mapped[Optional[str]] = mapped_column(String(100))

    # Metrics
    score: Mapped[int] = mapped_column(Integer, default=0)
    comments_count: Mapped[int] = mapped_column(Integer, default=0)

    # Status
    is_dead: Mapped[bool] = mapped_column(Boolean, default=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    # Dates
    posted_at: Mapped[Optional[datetime]] = mapped_column()

    # Extra data
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON)

    def __repr__(self) -> str:
        return f"<HackerNewsItem {self.hn_id}: {self.title[:30] if self.title else 'No title'}...>"


class RedditPost(Base, TimestampMixin):
    """Reddit post model."""

    __tablename__ = "reddit_posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    reddit_id: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)

    # Subreddit
    subreddit: Mapped[str] = mapped_column(String(100), nullable=False)

    # Content
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    selftext: Mapped[Optional[str]] = mapped_column(Text)
    url: Mapped[Optional[str]] = mapped_column(String(500))

    # Author
    author: Mapped[Optional[str]] = mapped_column(String(100))

    # Media
    thumbnail: Mapped[Optional[str]] = mapped_column(String(500))
    is_video: Mapped[bool] = mapped_column(Boolean, default=False)

    # Metrics
    score: Mapped[int] = mapped_column(Integer, default=0)
    upvote_ratio: Mapped[Optional[float]] = mapped_column()
    num_comments: Mapped[int] = mapped_column(Integer, default=0)
    num_awards: Mapped[int] = mapped_column(Integer, default=0)

    # Status
    is_nsfw: Mapped[bool] = mapped_column(Boolean, default=False)
    is_spoiler: Mapped[bool] = mapped_column(Boolean, default=False)
    is_stickied: Mapped[bool] = mapped_column(Boolean, default=False)

    # Flair
    flair_text: Mapped[Optional[str]] = mapped_column(String(100))

    # Dates
    posted_at: Mapped[Optional[datetime]] = mapped_column()

    # Extra data
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON)

    def __repr__(self) -> str:
        return f"<RedditPost r/{self.subreddit}: {self.title[:30]}...>"


class GitHubRepo(Base, TimestampMixin):
    """GitHub repository model."""

    __tablename__ = "github_repos"

    id: Mapped[int] = mapped_column(primary_key=True)
    github_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)

    # Basic Info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(500), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Owner
    owner: Mapped[str] = mapped_column(String(100), nullable=False)
    owner_type: Mapped[str] = mapped_column(String(20))  # User, Organization
    owner_avatar: Mapped[Optional[str]] = mapped_column(String(500))

    # URLs
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    homepage: Mapped[Optional[str]] = mapped_column(String(500))

    # Language & Topics
    language: Mapped[Optional[str]] = mapped_column(String(50))
    topics: Mapped[Optional[List[str]]] = mapped_column(JSON)

    # Metrics
    stars: Mapped[int] = mapped_column(Integer, default=0)
    forks: Mapped[int] = mapped_column(Integer, default=0)
    watchers: Mapped[int] = mapped_column(Integer, default=0)
    open_issues: Mapped[int] = mapped_column(Integer, default=0)

    # Activity
    default_branch: Mapped[Optional[str]] = mapped_column(String(100), default="main")
    is_fork: Mapped[bool] = mapped_column(Boolean, default=False)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)

    # License
    license_name: Mapped[Optional[str]] = mapped_column(String(100))

    # Trending info
    trending_rank: Mapped[Optional[int]] = mapped_column(Integer)
    stars_today: Mapped[int] = mapped_column(Integer, default=0)

    # Dates
    repo_created_at: Mapped[Optional[datetime]] = mapped_column()
    repo_updated_at: Mapped[Optional[datetime]] = mapped_column()
    pushed_at: Mapped[Optional[datetime]] = mapped_column()

    # Extra data
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON)

    def __repr__(self) -> str:
        return f"<GitHubRepo {self.full_name}>"


class Tweet(Base, TimestampMixin):
    """Twitter/X tweet model for AI-related content."""

    __tablename__ = "tweets"

    id: Mapped[int] = mapped_column(primary_key=True)
    tweet_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    # Content
    text: Mapped[str] = mapped_column(Text, nullable=False)

    # Author
    author_id: Mapped[str] = mapped_column(String(50), nullable=False)
    author_username: Mapped[str] = mapped_column(String(100), nullable=False)
    author_name: Mapped[Optional[str]] = mapped_column(String(255))
    author_profile_image: Mapped[Optional[str]] = mapped_column(String(500))
    author_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # Metrics
    likes: Mapped[int] = mapped_column(Integer, default=0)
    retweets: Mapped[int] = mapped_column(Integer, default=0)
    replies: Mapped[int] = mapped_column(Integer, default=0)
    quotes: Mapped[int] = mapped_column(Integer, default=0)
    impressions: Mapped[int] = mapped_column(Integer, default=0)

    # Media
    has_media: Mapped[bool] = mapped_column(Boolean, default=False)
    media_urls: Mapped[Optional[List[str]]] = mapped_column(JSON)

    # Topic/Search
    topic: Mapped[Optional[str]] = mapped_column(String(100))  # AI, ML, LLM, etc.
    search_query: Mapped[Optional[str]] = mapped_column(String(255))

    # Status
    is_retweet: Mapped[bool] = mapped_column(Boolean, default=False)
    is_reply: Mapped[bool] = mapped_column(Boolean, default=False)

    # Dates
    tweeted_at: Mapped[Optional[datetime]] = mapped_column()

    # Extra data
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON)

    def __repr__(self) -> str:
        return f"<Tweet {self.tweet_id}: {self.text[:30]}...>"
