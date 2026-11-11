
from pydantic import BaseModel, Field

from google_news_mcp.models.article import NewsArticle


class NewsSearchResponse(BaseModel):
    """Structured response returned by a Google News search."""

    query: str = Field(description="The original search query.")
    region: str = Field(description="Two-letter country code.")
    language: str = Field(description="Language used for the search.")
    count: int = Field(description="Number of articles returned.")
    articles: list[NewsArticle] = Field(
        description="List of matching news articles."
    )
