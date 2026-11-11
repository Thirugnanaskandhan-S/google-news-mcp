
from datetime import datetime

from pydantic import BaseModel, HttpUrl


class NewsArticle(BaseModel):
    """Represents a single news article returned by Google News."""

    title: str
    publisher: str
    published_at: datetime | None = None
    url: HttpUrl
