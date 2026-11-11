
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


settings = Settings()
