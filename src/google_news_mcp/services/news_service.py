
from google_news_mcp.config import settings
from google_news_mcp.models.article import NewsArticle
from google_news_mcp.providers.google_news import GoogleNewsProvider


class NewsService:
    """Provides application-level news functionality."""

    def __init__(
        self,
        provider: GoogleNewsProvider | None = None,
    ) -> None:
        self._provider = provider or GoogleNewsProvider()

    def _deduplicate(
        self,
        articles: list[NewsArticle],
    ) -> list[NewsArticle]:
        """Remove articles with duplicate URLs."""

        unique_articles: list[NewsArticle] = []
        seen_urls: set[str] = set()

        for article in articles:
            article_url = str(article.url).rstrip("/")

            if article_url in seen_urls:
                continue

            seen_urls.add(article_url)
            unique_articles.append(article)

        return unique_articles

    async def search_news(
        self,
        query: str,
        region: str = settings.default_region,
        language: str = settings.default_language,
        max_results: int = settings.default_max_results,
    ) -> list[NewsArticle]:
        """Search news by keywords."""

        normalized_query = query.strip()

        if not normalized_query:
            raise ValueError("Search query cannot be empty.")

        articles = await self._provider.search(
            query=normalized_query,
            region=region,
            language=language,
            max_results=max_results,
        )

        return self._deduplicate(articles)[:max_results]

    async def get_top_headlines(
        self,
        region: str = settings.default_region,
        language: str = settings.default_language,
        max_results: int = settings.default_max_results,
    ) -> list[NewsArticle]:
        """Retrieve general news headlines."""

        articles = await self._provider.get_top_headlines(
            region=region,
            language=language,
            max_results=max_results,
        )

        return self._deduplicate(articles)[:max_results]

    
    async def search_news_by_publisher(
        self,
        query: str,
        publisher: str,
        region: str = settings.default_region,
        language: str = settings.default_language,
        max_results: int = settings.default_max_results,
    ) -> list[NewsArticle]:
        """Search Google News articles from a specific publisher."""

        normalized_publisher = publisher.strip()

        if not normalized_publisher:
            raise ValueError("Publisher name cannot be empty.")

        combined_query = (
            f"{query.strip()} site:{normalized_publisher}"
        )

        articles = await self._provider.search(
            query=combined_query,
            region=region,
            language=language,
            max_results=max_results,
        )

        return self._deduplicate(articles)[:max_results]

