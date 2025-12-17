"""RSS News collector for AI news from multiple sources."""
from typing import Any, Dict, List, Optional
from datetime import datetime
import re
import feedparser
from .base import BaseCollector
from app.models.news import NewsSource


class RSSNewsCollector(BaseCollector):
    """Collector for RSS feeds from AI news sources."""

    # RSS Feed URLs for AI news sources
    FEEDS = {
        NewsSource.TECHCRUNCH: "https://techcrunch.com/category/artificial-intelligence/feed/",
        NewsSource.VENTUREBEAT: "https://venturebeat.com/category/ai/feed/",
        NewsSource.MIT_TECH_REVIEW: "https://www.technologyreview.com/topic/artificial-intelligence/feed",
        NewsSource.GOOGLE_AI: "https://blog.google/technology/ai/rss/",
        NewsSource.OPENAI: "https://openai.com/blog/rss/",
        NewsSource.ANTHROPIC: "https://www.anthropic.com/rss.xml",
        NewsSource.HUGGINGFACE: "https://huggingface.co/blog/feed.xml",
        NewsSource.TOWARDS_DATA_SCIENCE: "https://towardsdatascience.com/feed",
        NewsSource.KDNUGGETS: "https://www.kdnuggets.com/feed",
    }

    def __init__(self):
        super().__init__("rss_news")

    async def collect(
        self,
        sources: Optional[List[NewsSource]] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Collect news from RSS feeds."""
        sources_to_fetch = sources or list(self.FEEDS.keys())
        all_items = []

        for source in sources_to_fetch:
            if source not in self.FEEDS:
                continue

            feed_url = self.FEEDS[source]
            try:
                # feedparser handles fetching internally
                feed = feedparser.parse(feed_url)

                for entry in feed.entries:
                    entry["_source"] = source
                    all_items.append(entry)

                self.logger.info(f"Fetched {len(feed.entries)} items from {source.value}")
            except Exception as e:
                self.logger.error(f"Error fetching {source.value}: {e}")
                continue

        return all_items

    async def transform(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform RSS feed data to news article model format."""
        articles = []

        for item in raw_data:
            source = item.get("_source")

            # Extract content
            content = ""
            if hasattr(item, "content") and item.content:
                content = item.content[0].get("value", "")
            elif hasattr(item, "summary"):
                content = item.summary

            # Parse published date
            published_at = None
            if hasattr(item, "published_parsed") and item.published_parsed:
                try:
                    published_at = datetime(*item.published_parsed[:6])
                except Exception:
                    pass

            # Extract image URL from content or media
            image_url = self._extract_image(item, content)

            # Create unique external ID
            external_id = item.get("id") or item.get("link", "")

            article = {
                "external_id": external_id,
                "source": source,
                "title": item.get("title", ""),
                "slug": self._create_slug(item.get("title", "")),
                "summary": self._clean_html(item.get("summary", ""))[:500] if item.get("summary") else None,
                "content": self._clean_html(content) if content else None,
                "content_html": content,
                "author": item.get("author"),
                "url": item.get("link", ""),
                "image_url": image_url,
                "tags": [tag.get("term") for tag in item.get("tags", [])] if item.get("tags") else None,
                "published_at": published_at,
            }
            articles.append(article)

        return articles

    def _create_slug(self, title: str) -> str:
        """Create URL-friendly slug from title."""
        slug = title.lower()
        slug = re.sub(r"[^a-z0-9\s-]", "", slug)
        slug = re.sub(r"[\s_]+", "-", slug)
        slug = re.sub(r"-+", "-", slug)
        return slug.strip("-")[:550]

    def _clean_html(self, html: str) -> str:
        """Remove HTML tags from content."""
        clean = re.sub(r"<[^>]+>", "", html)
        clean = re.sub(r"\s+", " ", clean)
        return clean.strip()

    def _extract_image(self, item: Dict, content: str) -> Optional[str]:
        """Extract image URL from feed item or content."""
        # Check media_content
        if hasattr(item, "media_content") and item.media_content:
            for media in item.media_content:
                if media.get("medium") == "image" or media.get("type", "").startswith("image"):
                    return media.get("url")

        # Check media_thumbnail
        if hasattr(item, "media_thumbnail") and item.media_thumbnail:
            return item.media_thumbnail[0].get("url")

        # Check enclosures
        if hasattr(item, "enclosures") and item.enclosures:
            for enc in item.enclosures:
                if enc.get("type", "").startswith("image"):
                    return enc.get("href")

        # Try to extract from content
        if content:
            img_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', content)
            if img_match:
                return img_match.group(1)

        return None
