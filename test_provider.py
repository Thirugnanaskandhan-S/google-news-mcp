
import asyncio

from google_news_mcp.providers.google_news import GoogleNewsProvider


async def main():
    provider = GoogleNewsProvider()

    print("\nFetching top headlines...\n")

    articles = await provider.get_top_headlines(
        region="IN",
        language="en",
        max_results=5,
    )

    for index, article in enumerate(articles, start=1):
        print(f"{index}. {article.title}")
        print(f"   Publisher: {article.publisher}")
        print(f"   Published: {article.published_at}")
        print()


if __name__ == "__main__":
    asyncio.run(main())
