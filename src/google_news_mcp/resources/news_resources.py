
import json

from mcp.server import MCPServer


def register_news_resources(mcp: MCPServer) -> None:
    """Register Google News resources."""

    @mcp.resource(
        "news://regions",
        name="Supported News Regions",
        description="Lists supported Google News regions.",
        mime_type="application/json",
    )
    def get_supported_regions() -> str:
        regions = {
            "regions": [
                {"code": "IN", "name": "India", "language": "en"},
                {"code": "US", "name": "United States", "language": "en"},
                {"code": "GB", "name": "United Kingdom", "language": "en"},
                {"code": "CA", "name": "Canada", "language": "en"},
                {"code": "AU", "name": "Australia", "language": "en"},
            ]
        }

        return json.dumps(regions, indent=2)

    @mcp.resource(
        "news://categories",
        name="News Categories",
        description="Lists suggested news search categories.",
        mime_type="application/json",
    )
    def get_news_categories() -> str:
        categories = {
            "categories": [
                {"id": "technology", "name": "Technology"},
                {"id": "business", "name": "Business"},
                {"id": "politics", "name": "Politics"},
                {"id": "science", "name": "Science"},
                {"id": "health", "name": "Health"},
                {"id": "sports", "name": "Sports"},
                {"id": "entertainment", "name": "Entertainment"},
                {"id": "world", "name": "World News"},
            ]
        }

        return json.dumps(categories, indent=2)

    @mcp.resource(
        "news://about",
        name="Google News MCP Information",
        description="Provides information about this MCP server.",
        mime_type="application/json",
    )
    def get_server_information() -> str:
        information = {
            "name": "Google News MCP",
            "version": "0.1.0",
            "description": "An MCP server for retrieving Google News articles.",
            "data_source": "Google News RSS",
            "capabilities": {
                "tools": [
                    "search_news",
                    "get_top_headlines",
                    "search_news_by_publisher",
                ],
                "resources": [
                    "news://regions",
                    "news://categories",
                    "news://about",
                ],
            },
        }

        return json.dumps(information, indent=2)
