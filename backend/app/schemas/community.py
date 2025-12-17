"""Community content schemas (HN, Reddit, GitHub)."""
from datetime import datetime
from typing import Optional, List
from .common import BaseResponse, PaginatedResponse


class HackerNewsResponse(BaseResponse):
    """Hacker News item response schema."""

    id: int
    hn_id: int
    item_type: str
    title: Optional[str] = None
    url: Optional[str] = None
    text: Optional[str] = None
    author: Optional[str] = None
    score: int = 0
    comments_count: int = 0
    posted_at: Optional[datetime] = None
    created_at: datetime


class HackerNewsListResponse(PaginatedResponse[HackerNewsResponse]):
    """Paginated HN list response."""

    pass


class RedditPostResponse(BaseResponse):
    """Reddit post response schema."""

    id: int
    reddit_id: str
    subreddit: str
    title: str
    selftext: Optional[str] = None
    url: Optional[str] = None
    author: Optional[str] = None
    thumbnail: Optional[str] = None
    is_video: bool = False
    score: int = 0
    upvote_ratio: Optional[float] = None
    num_comments: int = 0
    num_awards: int = 0
    flair_text: Optional[str] = None
    posted_at: Optional[datetime] = None
    created_at: datetime


class RedditListResponse(PaginatedResponse[RedditPostResponse]):
    """Paginated Reddit list response."""

    pass


class GitHubRepoResponse(BaseResponse):
    """GitHub repository response schema."""

    id: int
    github_id: int
    name: str
    full_name: str
    description: Optional[str] = None
    owner: str
    owner_type: str
    owner_avatar: Optional[str] = None
    url: str
    homepage: Optional[str] = None
    language: Optional[str] = None
    topics: Optional[List[str]] = None
    stars: int = 0
    forks: int = 0
    watchers: int = 0
    open_issues: int = 0
    default_branch: str = "main"
    is_fork: bool = False
    is_archived: bool = False
    license_name: Optional[str] = None
    trending_rank: Optional[int] = None
    stars_today: int = 0
    repo_created_at: Optional[datetime] = None
    repo_updated_at: Optional[datetime] = None
    created_at: datetime


class GitHubListResponse(PaginatedResponse[GitHubRepoResponse]):
    """Paginated GitHub repos list response."""

    pass


class TweetResponse(BaseResponse):
    """Tweet response schema."""

    id: int
    tweet_id: str
    text: str
    author_id: str
    author_username: str
    author_name: Optional[str] = None
    author_profile_image: Optional[str] = None
    author_verified: bool = False
    likes: int = 0
    retweets: int = 0
    replies: int = 0
    quotes: int = 0
    impressions: int = 0
    has_media: bool = False
    media_urls: Optional[List[str]] = None
    topic: Optional[str] = None
    is_retweet: bool = False
    is_reply: bool = False
    tweeted_at: Optional[datetime] = None
    created_at: datetime


class TweetListResponse(PaginatedResponse[TweetResponse]):
    """Paginated tweets list response."""

    pass
