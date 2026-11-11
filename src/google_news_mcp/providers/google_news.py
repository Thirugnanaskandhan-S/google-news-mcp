
from datetime import datetime
from email.utils import parsedate_to_datetime

import feedparser
import httpx
from pydantic import ValidationError

from google_news_mcp.config import settings
from google_news_mcp.models.article import NewsArticle


class GoogleNewsProvider:
    """Fetches and parses news articles from Google News RSS."""

    def __init__(self) -> None:
        self.base_url = settings.google_news_base_url
        self.timeout = settings.request_timeout

    async def search(
        self,
        query: str,
        region: str = settings.default_region,
        language: str = settings.default_language,
        max_results: int = settings.default_max_results,
    ) -> list[NewsArticle]:
        """Search Google News using keywords."""

        if not query.strip():
            raise ValueError("Search query cannot be empty.")

        self._validate_max_results(max_results)

        params = {
            "q": query.strip(),
            "hl": f"{language}-{region}",
            "gl": region,
            "ceid": f"{region}:{language}",
        }

        return await self._fetch_articles(
            endpoint=f"{self.base_url}/search",
            params=params,
            max_results=max_results,
        )

    async def get_top_headlines(
        self,
        region: str = settings.default_region,
        language: str = settings.default_language,
        max_results: int = settings.default_max_results,
    ) -> list[NewsArticle]:
        """Retrieve general Google News headlines."""

        self._validate_max_results(max_results)

        params = {
            "hl": f"{language}-{region}",
            "gl": region,
            "ceid": f"{region}:{language}",
        }

        return await self._fetch_articles(
            endpoint=self.base_url,
            params=params,
            max_results=max_results,
        )

    def _validate_max_results(self, max_results: int) -> None:
        if not 1 <= max_results <= settings.maximum_results:
            raise ValueError(
                f"max_results must be between 1 and "
                f"{settings.maximum_results}."
            )

    async def _fetch_articles(
        self,
        endpoint: str,
        params: dict[str, str],
        max_results: int,
    ) -> list[NewsArticle]:
        """Fetch an RSS feed and convert entries into validated articles."""

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                headers={"User-Agent": "GoogleNewsMCP/0.1"},
            ) as client:
                response = await client.get(endpoint, params=params)
                response.raise_for_status()

        except httpx.HTTPError as exc:
            raise RuntimeError(
                f"Failed to retrieve Google News: {exc}"
            ) from exc

        feed = feedparser.parse(response.content)

        if feed.bozo and not feed.entries:
            raise ValueError("Google News returned an invalid RSS feed.")

        articles: list[NewsArticle] = []

        for entry in feed.entries[:max_results]:
            title = entry.get("title")
            article_url = entry.get("link")

            if not title or not article_url:
                continue

            source = entry.get("source") or {}
            publisher = source.get("title", "Unknown publisher")

            published_at: datetime | None = None
            published = entry.get("published")

            if published:
                try:
                    published_at = parsedate_to_datetime(published)
                except (TypeError, ValueError, OverflowError):
                    published_at = None

            try:
                article = NewsArticle(
                    title=title,
                    publisher=publisher,
                    published_at=published_at,
                    url=article_url,
                )
                articles.append(article)

            except ValidationError:
                continue

        return articles
