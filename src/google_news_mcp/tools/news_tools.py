
from typing import Annotated

from mcp.server import MCPServer
from pydantic import Field

from google_news_mcp.models.search import NewsSearchResponse
from google_news_mcp.services.news_service import NewsService


def register_news_tools(
    mcp: MCPServer,
    news_service: NewsService,
) -> None:
    """Register Google News tools with the MCP server."""

    @mcp.tool()
    async def search_news(
        query: Annotated[
            str,
            Field(
                min_length=2,
                max_length=200,
                description="Topic or keywords to search for in Google News.",
            ),
        ],
        region: str = "IN",
        language: str = "en",
        max_results: Annotated[
            int,
            Field(ge=1, le=50),
        ] = 10,
    ) -> NewsSearchResponse:
        """Search Google News for articles matching a topic."""

        articles = await news_service.search_news(
            query=query,
            region=region.upper(),
            language=language.lower(),
            max_results=max_results,
        )

        return NewsSearchResponse(
            query=query.strip(),
            region=region.upper(),
            language=language.lower(),
            count=len(articles),
            articles=articles,
        )

    @mcp.tool()
    async def get_top_headlines(
        region: str = "IN",
        language: str = "en",
        max_results: Annotated[
            int,
            Field(ge=1, le=50),
        ] = 10,
    ) -> NewsSearchResponse:
        """Retrieve the latest general headlines from Google News."""

        articles = await news_service.get_top_headlines(
            region=region.upper(),
            language=language.lower(),
            max_results=max_results,
        )

        return NewsSearchResponse(
            query="Top headlines",
            region=region.upper(),
            language=language.lower(),
            count=len(articles),
            articles=articles,
        )

    
    @mcp.tool()
    async def search_news_by_publisher(
        query: Annotated[
            str,
            Field(
                min_length=2,
                max_length=200,
                description="Topic to search for.",
            ),
        ],
        publisher: Annotated[
            str,
            Field(
                min_length=2,
                max_length=100,
                description="Publisher domain, such as bbc.com or reuters.com.",
            ),
        ],
        region: str = "IN",
        language: str = "en",
        max_results: Annotated[
            int,
            Field(ge=1, le=50),
        ] = 10,
    ) -> NewsSearchResponse:
        """Search Google News for articles from a specific publisher."""

        articles = await news_service.search_news_by_publisher(
            query=query,
            publisher=publisher,
            region=region.upper(),
            language=language.lower(),
            max_results=max_results,
        )

        return NewsSearchResponse(
            query=query.strip(),
            region=region.upper(),
            language=language.lower(),
            count=len(articles),
            articles=articles,
        )

