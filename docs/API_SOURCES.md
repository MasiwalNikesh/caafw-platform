# API Sources Documentation

## Overview

This document lists all data sources used by the AI Community Platform, including APIs, RSS feeds, and scraping targets.

---

## 1. News & Blogs

### RSS Feeds (No API Key Required)

| Source | Feed URL | Update Frequency | Status |
|--------|----------|------------------|--------|
| TechCrunch AI | `https://techcrunch.com/category/artificial-intelligence/feed/` | Hourly | Active |
| VentureBeat AI | `https://venturebeat.com/category/ai/feed/` | Hourly | Active |
| MIT Tech Review | `https://www.technologyreview.com/topic/artificial-intelligence/feed` | Daily | Active |
| Google AI Blog | `https://blog.google/technology/ai/rss/` | Weekly | Active |
| OpenAI Blog | `https://openai.com/blog/rss/` | Weekly | Active |
| Anthropic Blog | `https://www.anthropic.com/rss.xml` | Weekly | Active |
| Hugging Face Blog | `https://huggingface.co/blog/feed.xml` | Weekly | Active |
| Towards Data Science | `https://towardsdatascience.com/feed` | Daily | Active |
| KDnuggets | `https://www.kdnuggets.com/feed` | Daily | Active |
| **DeepMind Blog** | `https://deepmind.google/blog/rss.xml` | Weekly | **NEW** |
| **Meta AI Blog** | `https://ai.meta.com/blog/rss/` | Weekly | **NEW** |
| **The Batch (Andrew Ng)** | `https://www.deeplearning.ai/the-batch/feed/` | Weekly | **NEW** |
| **The Gradient** | `https://thegradient.pub/rss/` | Weekly | **NEW** |
| **Distill.pub** | `https://distill.pub/rss.xml` | Monthly | **NEW** |
| **W&B Blog** | `https://wandb.ai/fully-connected/rss.xml` | Weekly | **NEW** |
| **NVIDIA AI Blog** | `https://blogs.nvidia.com/feed/` | Weekly | **NEW** |
| **AWS AI Blog** | `https://aws.amazon.com/blogs/machine-learning/feed/` | Weekly | **NEW** |
| **Microsoft AI Blog** | `https://blogs.microsoft.com/ai/feed/` | Weekly | **NEW** |

---

## 2. Research Papers

### arXiv API (No Key Required)

| Endpoint | Description | Rate Limit |
|----------|-------------|------------|
| `http://export.arxiv.org/api/query` | Search/fetch papers | 1 req/3 sec |

**Categories:**
- `cs.AI` - Artificial Intelligence
- `cs.LG` - Machine Learning
- `cs.CL` - Computation and Language (NLP)
- `cs.CV` - Computer Vision
- `cs.NE` - Neural and Evolutionary Computing
- `stat.ML` - Machine Learning (Statistics)

### Semantic Scholar API (No Key Required)

| Endpoint | Description | Rate Limit |
|----------|-------------|------------|
| `https://api.semanticscholar.org/graph/v1/paper/search` | Search papers | 100 req/5 min |
| `https://api.semanticscholar.org/graph/v1/paper/{paper_id}` | Paper details | 100 req/5 min |

**Example:**
```bash
curl "https://api.semanticscholar.org/graph/v1/paper/search?query=large+language+models&limit=10&fields=title,authors,year,citationCount,abstract"
```

### Papers With Code API (No Key Required)

| Endpoint | Description | Rate Limit |
|----------|-------------|------------|
| `https://paperswithcode.com/api/v1/papers/` | List papers | Reasonable |
| `https://paperswithcode.com/api/v1/repositories/` | Code repos | Reasonable |

**Example:**
```bash
curl "https://paperswithcode.com/api/v1/papers/?ordering=-published&items_per_page=20"
```

### Hugging Face Daily Papers (No Key Required)

| Endpoint | Description | Rate Limit |
|----------|-------------|------------|
| `https://huggingface.co/api/daily_papers` | Trending papers | Generous |

---

## 3. GitHub Repositories

### GitHub API (API Key Recommended)

| Endpoint | Description | Rate Limit |
|----------|-------------|------------|
| `https://api.github.com/search/repositories` | Search repos | 10 req/min (unauth), 30 req/min (auth) |
| `https://api.github.com/repos/{owner}/{repo}` | Repo details | 60 req/hr (unauth), 5000 req/hr (auth) |

**Environment Variable:** `GITHUB_TOKEN`

**Get Token:** https://github.com/settings/tokens

---

## 4. Job Listings

### Greenhouse Boards API (No Key Required)

Direct access to company job boards:

| Company | Endpoint |
|---------|----------|
| **OpenAI** | `https://boards-api.greenhouse.io/v1/boards/openai/jobs` |
| **Anthropic** | `https://boards-api.greenhouse.io/v1/boards/anthropic/jobs` |
| **Scale AI** | `https://boards-api.greenhouse.io/v1/boards/scaleai/jobs` |
| **Databricks** | `https://boards-api.greenhouse.io/v1/boards/databricks/jobs` |
| **Stripe** | `https://boards-api.greenhouse.io/v1/boards/stripe/jobs` |
| **Figma** | `https://boards-api.greenhouse.io/v1/boards/figma/jobs` |
| **Notion** | `https://boards-api.greenhouse.io/v1/boards/notion/jobs` |
| **Ramp** | `https://boards-api.greenhouse.io/v1/boards/ramp/jobs` |

### Lever Postings API (No Key Required)

| Company | Endpoint |
|---------|----------|
| **Hugging Face** | `https://api.lever.co/v0/postings/huggingface` |
| **Cohere** | `https://api.lever.co/v0/postings/cohere` |
| **Stability AI** | `https://api.lever.co/v0/postings/stabilityai` |
| **Weights & Biases** | `https://api.lever.co/v0/postings/wandb` |
| **Anyscale** | `https://api.lever.co/v0/postings/anyscale` |
| **Modal** | `https://api.lever.co/v0/postings/modal` |
| **Replicate** | `https://api.lever.co/v0/postings/replicate` |

### RemoteOK API (No Key Required)

| Endpoint | Description |
|----------|-------------|
| `https://remoteok.com/api` | Remote tech jobs (JSON) |

### Remotive API (No Key Required)

| Endpoint | Description |
|----------|-------------|
| `https://remotive.com/api/remote-jobs?category=software-dev` | Remote jobs |

### Adzuna API (API Key Required)

| Endpoint | Description | Rate Limit |
|----------|-------------|------------|
| `https://api.adzuna.com/v1/api/jobs/{country}/search/1` | Job search | 250 req/day |

**Environment Variables:** `ADZUNA_APP_ID`, `ADZUNA_API_KEY`

**Get Keys:** https://developer.adzuna.com/

---

## 5. Products & Tools

### Product Hunt API (API Key Required)

| Endpoint | Description | Rate Limit |
|----------|-------------|------------|
| `https://api.producthunt.com/v2/api/graphql` | GraphQL API | 500 req/day |

**Environment Variables:** `PRODUCT_HUNT_TOKEN`

**Get Token:** https://www.producthunt.com/v2/oauth/applications

### Hugging Face Models API (No Key Required)

| Endpoint | Description |
|----------|-------------|
| `https://huggingface.co/api/models` | List models |
| `https://huggingface.co/api/models?sort=downloads` | Popular models |

---

## 6. Events & Conferences

### Luma API (Scraping)

| URL | Description |
|-----|-------------|
| `https://lu.ma/ai` | AI events listing |

### Eventbrite API (API Key Required)

| Endpoint | Description |
|----------|-------------|
| `https://www.eventbriteapi.com/v3/events/search/` | Search events |

**Environment Variable:** `EVENTBRITE_API_KEY`

### Meetup API (OAuth Required)

| Endpoint | Description |
|----------|-------------|
| `https://api.meetup.com/find/upcoming_events` | Find events |

---

## 7. Social & Community

### HackerNews API (No Key Required)

| Endpoint | Description |
|----------|-------------|
| `https://hacker-news.firebaseio.com/v0/topstories.json` | Top stories |
| `https://hacker-news.firebaseio.com/v0/newstories.json` | New stories |
| `https://hacker-news.firebaseio.com/v0/item/{id}.json` | Item details |

### Reddit API (API Key Required for higher limits)

| Endpoint | Description | Rate Limit |
|----------|-------------|------------|
| `https://www.reddit.com/r/MachineLearning.json` | ML subreddit | 60 req/min |
| `https://www.reddit.com/r/artificial.json` | AI subreddit | 60 req/min |
| `https://www.reddit.com/r/LocalLLaMA.json` | Local LLM subreddit | 60 req/min |

### Twitter/X API (API Key Required)

| Endpoint | Description | Rate Limit |
|----------|-------------|------------|
| `https://api.twitter.com/2/tweets/search/recent` | Search tweets | 450 req/15 min |

**Environment Variables:** `TWITTER_BEARER_TOKEN`

---

## 8. Video Content

### YouTube Data API (API Key Required)

| Endpoint | Description | Rate Limit |
|----------|-------------|------------|
| `https://www.googleapis.com/youtube/v3/search` | Search videos | 10,000 units/day |
| `https://www.googleapis.com/youtube/v3/videos` | Video details | 10,000 units/day |

**Environment Variable:** `YOUTUBE_API_KEY`

**Get Key:** https://console.cloud.google.com/apis/credentials

**Recommended Channels:**
- Two Minute Papers
- Yannic Kilcher
- AI Explained
- Andrej Karpathy
- 3Blue1Brown
- StatQuest
- sentdex

---

## 9. Investment & Funding

### Crunchbase API (API Key Required)

| Endpoint | Description | Rate Limit |
|----------|-------------|------------|
| `https://api.crunchbase.com/api/v4/entities/organizations` | Company data | Varies by plan |

**Environment Variable:** `CRUNCHBASE_API_KEY`

### PitchBook (Enterprise Only)

Requires enterprise subscription.

### Alternative: TechCrunch RSS

| Feed | Description |
|------|-------------|
| `https://techcrunch.com/category/startups/feed/` | Startup news including funding |

---

## 10. MCP Servers

### Smithery API

| Endpoint | Description |
|----------|-------------|
| `https://smithery.ai/api/servers` | MCP server registry |

### GitHub MCP Registry

| URL | Description |
|-----|-------------|
| `https://github.com/modelcontextprotocol/servers` | Official MCP servers |
| `https://api.github.com/search/repositories?q=topic:mcp-server` | Community servers |

---

## Rate Limiting Strategy

### Priority Tiers

| Tier | Sources | Fetch Frequency |
|------|---------|-----------------|
| **High** | arXiv, Greenhouse/Lever Jobs, HackerNews | Every 6 hours |
| **Medium** | RSS Feeds, GitHub, Papers With Code | Every 12 hours |
| **Low** | YouTube, Events, Social | Every 24 hours |

### Cron Schedule (No Celery/Redis Required)

```bash
# /etc/cron.d/ai-platform-collectors

# High priority - every 6 hours
0 */6 * * * cd /app && python -m app.collectors.run --sources=arxiv,jobs,hackernews

# Medium priority - every 12 hours
0 */12 * * * cd /app && python -m app.collectors.run --sources=rss,github,papers

# Low priority - daily
0 4 * * * cd /app && python -m app.collectors.run --sources=youtube,events,social
```

---

## Environment Variables Summary

```bash
# Required for full functionality
GITHUB_TOKEN=                    # GitHub API
YOUTUBE_API_KEY=                 # YouTube Data API
PRODUCT_HUNT_TOKEN=              # Product Hunt API

# Optional - enhances data
TWITTER_BEARER_TOKEN=            # Twitter/X API
ADZUNA_APP_ID=                   # Adzuna Jobs
ADZUNA_API_KEY=                  # Adzuna Jobs
CRUNCHBASE_API_KEY=              # Investment data

# No API key needed
# - arXiv, Semantic Scholar, Papers With Code
# - Hugging Face APIs
# - Greenhouse/Lever job boards
# - HackerNews, Reddit (basic)
# - All RSS feeds
```

---

## Data Quality Notes

### Verified/Authoritative Sources
- arXiv (official research)
- Company blogs (OpenAI, Anthropic, DeepMind, etc.)
- Greenhouse/Lever (real job postings)
- Papers With Code (peer-reviewed + code)

### Aggregated/Community Sources
- HackerNews (community curated)
- Reddit (community discussions)
- Product Hunt (community voted)

### Requires Admin Review
- All scraped content
- User-submitted content
- Social media posts
