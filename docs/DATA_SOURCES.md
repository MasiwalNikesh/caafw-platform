# AI Community Platform - Data Sources Configuration

This document describes all integrated data sources, their configuration, and how to add new ones.

---

## Quick Overview

| Category | Active Sources | Total |
|----------|---------------|-------|
| **API Sources** | 10 | 11 |
| **RSS Feeds** | 18 | 18 |
| **Total** | **28** | **29** |

---

## Active Data Sources

### API Sources (10 Active)

| Source | Slug | API Key Required | Fetch Interval | Data Type |
|--------|------|------------------|----------------|-----------|
| **arXiv AI** | `arxiv-ai` | No | 60 min | Research papers |
| **Hacker News** | `hackernews` | No | 30 min | Tech discussions |
| **GitHub Trending** | `github-trending` | No (recommended) | 60 min | AI repositories |
| **Papers With Code** | `papers-with-code` | No | 60 min | ML papers + code |
| **Semantic Scholar** | `semantic-scholar` | No (optional) | 120 min | Paper metadata |
| **MCP Registry** | `mcp-registry` | No | 1440 min | MCP servers |
| **The Muse Jobs** | `themuse-jobs` | No (optional) | 120 min | Job listings |
| **Adzuna Jobs** | `adzuna-jobs` | Yes | 120 min | Job listings |
| **YouTube AI** | `youtube-ai` | Yes | 180 min | Learning videos |
| **Product Hunt AI** | `producthunt-ai` | Yes | 60 min | AI products |

### RSS Feeds (18 Active)

| Source | Slug | Fetch Interval | Content Type |
|--------|------|----------------|--------------|
| **Anthropic News** | `anthropic-news` | 120 min | Company blog |
| **OpenAI Blog** | `openai-blog` | 120 min | Company blog |
| **DeepMind Blog** | `deepmind-blog` | 120 min | Company blog |
| **Google AI Blog** | `google-ai-blog` | 120 min | Company blog |
| **Hugging Face Blog** | `huggingface-blog` | 120 min | Company blog |
| **TechCrunch AI** | `techcrunch-ai` | 60 min | Tech news |
| **VentureBeat AI** | `venturebeat-ai` | 60 min | Tech news |
| **MIT Technology Review** | `mit-tech-review-ai` | 120 min | Tech news |
| **Towards Data Science** | `towards-data-science` | 60 min | Tutorials |
| **KDnuggets** | `kdnuggets` | 120 min | ML news |
| **Machine Learning Mastery** | `ml-mastery` | 120 min | Tutorials |
| **The Batch** | `the-batch` | 1440 min | Newsletter |
| **Import AI** | `import-ai` | 1440 min | Newsletter |
| **The Gradient** | `the-gradient` | 1440 min | Research |
| **AI Alignment Forum** | `ai-alignment` | 120 min | AI safety |
| **LessWrong AI** | `lesswrong-ai` | 120 min | AI discussions |
| **RemoteOK AI Jobs** | `remoteok-ai` | 60 min | Remote jobs |
| **Y Combinator** | `ycombinator-ai` | 30 min | Startup news |

### Inactive Sources (Need API Keys)

| Source | Slug | Keys Needed |
|--------|------|-------------|
| **Reddit ML** | `reddit-ml` | `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET` |

---

## Environment Variables

Add these to `/backend/.env`:

```bash
# === CONFIGURED ===

# Products
PRODUCT_HUNT_CLIENT_ID=your_client_id
PRODUCT_HUNT_CLIENT_SECRET=your_client_secret
PRODUCT_HUNT_TOKEN=your_token

# Social Media
TWITTER_BEARER_TOKEN=your_bearer_token
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret

# Learning
YOUTUBE_API_KEY=your_youtube_api_key

# Jobs
ADZUNA_APP_ID=your_app_id
ADZUNA_API_KEY=your_api_key

# === OPTIONAL ===

# Developer (higher rate limits)
GITHUB_TOKEN=your_github_token

# Jobs (enhanced)
THE_MUSE_API_KEY=your_muse_key

# Research (higher rate limits)
SEMANTIC_SCHOLAR_API_KEY=your_key

# Investment data
CRUNCHBASE_API_KEY=your_key

# Events
EVENTBRITE_API_KEY=your_key

# Social (not yet enabled)
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
```

---

## Collectors Architecture

### Location
All collectors are in `/backend/app/collectors/`

### Available Collectors

| Collector | File | Data Model |
|-----------|------|------------|
| `ProductHuntCollector` | `product_hunt.py` | Products |
| `RSSNewsCollector` | `rss_news.py` | News Articles |
| `HackerNewsCollector` | `hackernews.py` | HN Items |
| `ArxivCollector` | `arxiv.py` | Research Papers |
| `GitHubCollector` | `github.py` | GitHub Repos |
| `AdzunaCollector` | `jobs.py` | Jobs |
| `TheMuseCollector` | `jobs.py` | Jobs |
| `YouTubeCollector` | `youtube.py` | Learning Resources |
| `MCPCollector` | `mcp.py` | MCP Servers |
| `TwitterCollector` | `twitter.py` | Tweets |
| `AIInvestmentsCollector` | `ai_investments.py` | Companies & Funding |

### Base Collector

All collectors extend `BaseCollector` which provides:
- HTTP client with retry logic
- Rate limiting
- Error handling
- Logging

```python
from app.collectors.base import BaseCollector

class MyCollector(BaseCollector):
    def __init__(self):
        super().__init__("my_source")

    async def collect(self, **kwargs) -> List[Dict]:
        # Fetch data from source
        pass

    async def transform(self, raw_data: List[Dict]) -> List[Dict]:
        # Transform to model format
        pass
```

---

## Adding New Sources

### 1. Add RSS Feed (Easiest)

```sql
INSERT INTO api_sources (name, slug, source_type, url, is_active, auto_approve, fetch_frequency)
VALUES ('Source Name', 'source-slug', 'rss', 'https://example.com/feed.xml', true, false, 60);
```

### 2. Add API Source

1. Create collector in `/backend/app/collectors/`
2. Add to `__init__.py`
3. Add environment variables to `config.py`
4. Insert source record:

```sql
INSERT INTO api_sources (name, slug, source_type, url, is_active, requires_api_key, fetch_frequency)
VALUES ('API Source', 'api-slug', 'api', 'https://api.example.com', true, true, 60);
```

---

## Data Collection Schedule

| Frequency | Sources |
|-----------|---------|
| **30 min** | Hacker News, Y Combinator |
| **60 min** | arXiv, GitHub, Papers With Code, Product Hunt, TechCrunch, VentureBeat, Towards Data Science, RemoteOK |
| **120 min** | Adzuna, The Muse, Semantic Scholar, Company blogs, ML news |
| **180 min** | YouTube |
| **1440 min (daily)** | MCP Registry, Newsletters (The Batch, Import AI, The Gradient) |

---

## API Documentation Links

| Service | Documentation |
|---------|---------------|
| Product Hunt | https://api.producthunt.com/v2/docs |
| YouTube Data API | https://developers.google.com/youtube/v3 |
| GitHub API | https://docs.github.com/en/rest |
| Adzuna | https://developer.adzuna.com/docs |
| The Muse | https://www.themuse.com/developers/api/v2 |
| arXiv | https://arxiv.org/help/api |
| Semantic Scholar | https://api.semanticscholar.org/ |
| Twitter/X | https://developer.twitter.com/en/docs |
| Reddit | https://www.reddit.com/dev/api |

---

## Troubleshooting

### Source Not Collecting Data

1. Check if source is active:
   ```sql
   SELECT * FROM api_sources WHERE slug = 'source-slug';
   ```

2. Check for API key:
   ```bash
   grep "API_KEY" /backend/.env
   ```

3. Check collector logs:
   ```bash
   tail -f /backend/logs/collectors.log
   ```

### Rate Limiting

- GitHub: 60 req/hr (unauthenticated), 5000 req/hr (with token)
- YouTube: 10,000 units/day
- Adzuna: 500 req/day (free tier)
- Twitter: Varies by plan

---

*Last updated: December 2024*
