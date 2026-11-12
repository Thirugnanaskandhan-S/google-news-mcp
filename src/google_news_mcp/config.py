
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Application-wide configuration."""

    google_news_base_url: str = "https://news.google.com/rss"
    default_region: str = "IN"
    default_language: str = "en"
    default_max_results: int = 10
    maximum_results: int = 50
    request_timeout: float = 15.0

    # Gemini orchestration (the API key itself is read from GEMINI_API_KEY).
    gemini_model: str = "gemini-3.5-flash-lite"
    gemini_max_tool_rounds: int = 5
    gemini_timeout_ms: int = 45_000
    gemini_max_articles: int = 20


settings = Settings()
